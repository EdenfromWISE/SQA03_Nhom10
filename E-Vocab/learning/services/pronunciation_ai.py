import os
import re
import shutil
import difflib
import tempfile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
import torch
import librosa
from transformers import AutoProcessor, AutoModelForCTC
from g2p_en import G2p
from pydub import AudioSegment


class PronunciationAssessor:
    def __init__(self):
        print(">>> [AI] ĐANG TẢI G2P (Phoneme Model)...")
        self.g2p = G2p()
        MODEL_ID = "facebook/wav2vec2-base-960h"
        print(f">>> [AI] ĐANG TẢI MÔ HÌNH: {MODEL_ID}...")
        self.processor = AutoProcessor.from_pretrained(MODEL_ID)
        self.model = AutoModelForCTC.from_pretrained(MODEL_ID)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if self.device.type == 'cpu':
            print(">>> [AI] Đang nén model (Quantization) để chạy nhanh hơn trên CPU...")
            try:
                # Nén các lớp Linear từ float32 (nặng) xuống int8 (nhẹ)
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
                print(">>> [AI] Nén model thành công!")
            except Exception as e:
                print(f">>> [AI-WARNING] Không thể nén model: {e}")
                print(">>> [AI] Sẽ chạy bằng model gốc (chậm hơn).")
        self.model.to(self.device)
        # Tìm FFmpeg executable
        self.ffmpeg_path = self._find_ffmpeg()
        if self.ffmpeg_path:
            AudioSegment.converter = self.ffmpeg_path
            print(f">>> [AI] Đã trỏ pydub dùng FFmpeg tại: {self.ffmpeg_path}")
        else:
            print(">>> [AI] WARNING: Không tìm thấy FFmpeg. Một số định dạng audio có thể không hoạt động.")
            print(">>> [AI] Vui lòng cài đặt FFmpeg và đặt vào PATH hoặc chỉ định đường dẫn trong biến môi trường FFMPEG_PATH")
            print(">>> [AI] Chỉ file WAV sẽ hoạt động mà không cần FFmpeg.")
        
        print(f">>> [AI] MÔ HÌNH ĐÃ SẴN SÀNG (chạy trên {self.device}).")
    
    def _find_ffmpeg(self):
        """Tìm đường dẫn FFmpeg executable."""
        # 1. Kiểm tra biến môi trường FFMPEG_PATH
        ffmpeg_path = os.environ.get('FFMPEG_PATH')
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            return ffmpeg_path
        
        # 2. Kiểm tra trong PATH
        ffmpeg_in_path = shutil.which('ffmpeg')
        if ffmpeg_in_path:
            return ffmpeg_in_path
        
        # 3. Kiểm tra các đường dẫn phổ biến trên Windows
        common_paths = [
            r"D:\ffmpeg\ffmpeg\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            r"/usr/bin/ffmpeg",
            os.path.join(os.path.expanduser("~"), "ffmpeg", "bin", "ffmpeg.exe"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # 4. Kiểm tra trong thư mục hiện tại hoặc venv
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(current_dir, "ffmpeg", "bin", "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
        
        return None

    def _transcribe_audio(self, audio_path):
        # Kiểm tra file có tồn tại không
        if not os.path.exists(audio_path):
            print(f"[AI-LỖI] _transcribe_audio: File không tồn tại: {audio_path}")
            return ""
        
        # Xác định định dạng đầu vào
        ext = os.path.splitext(audio_path)[1].lower()
        
        # Nếu file đã là WAV, thử load trực tiếp bằng librosa (không cần FFmpeg)
        if ext == ".wav":
            try:
                speech, rate = librosa.load(audio_path, sr=16000)
                input_values = self.processor(
                    speech, sampling_rate=16000, return_tensors="pt"
                ).input_values
                with torch.no_grad():
                    logits = self.model(input_values.to(self.device)).logits
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.processor.decode(predicted_ids[0])
                return transcription.lower()
            except Exception as e:
                print(f"[AI-LỖI] _transcribe_audio (WAV direct): {e}")
                # Fallback về cách convert bằng pydub
        
        # Tạo đường dẫn file WAV (thay extension hoặc thêm .wav)
        base_path = os.path.splitext(audio_path)[0]
        wav_path = base_path + ".wav"
        
        # Kiểm tra FFmpeg có sẵn không (chỉ cần cho các format không phải WAV)
        if ext != ".wav" and not self.ffmpeg_path:
            print(f"[AI-LỖI] _transcribe_audio: FFmpeg không được cấu hình. Không thể convert file {ext}")
            print(f"[AI-LỖI] Chỉ file WAV được hỗ trợ mà không cần FFmpeg.")
            return ""
        
        try:
            # Xác định format
            fmt = None
            if ext in (".webm", ".weba"):
                fmt = "webm"
            elif ext in (".ogg", ".oga"):
                fmt = "ogg"
            elif ext == ".wav":
                fmt = "wav"
            elif ext in (".mp3", ".m4a"):
                fmt = ext[1:]  # Bỏ dấu chấm

            # Đọc file bằng pydub với format chỉ định
            if fmt:
                sound = AudioSegment.from_file(audio_path, format=fmt)
            else:
                sound = AudioSegment.from_file(audio_path)

            # Chuẩn hóa về 16kHz mono
            sound = sound.set_frame_rate(16000)
            sound = sound.set_channels(1)
            sound.export(wav_path, format="wav")

            # Kiểm tra file WAV đã được tạo
            if not os.path.exists(wav_path):
                print(f"[AI-LỖI] _transcribe_audio: Không thể tạo file WAV: {wav_path}")
                return ""

            # Load và suy luận ASR
            speech, rate = librosa.load(wav_path, sr=16000)
            input_values = self.processor(
                speech, sampling_rate=16000, return_tensors="pt"
            ).input_values
            with torch.no_grad():
                logits = self.model(input_values.to(self.device)).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.decode(predicted_ids[0])
            return transcription.lower()
        except FileNotFoundError as e:
            # Lỗi FFmpeg không tìm thấy
            print(f"[AI-LỖI] _transcribe_audio: FFmpeg không tìm thấy. Vui lòng cài đặt FFmpeg.")
            print(f"[AI-LỖI] Chi tiết: {e}")
            return ""
        except Exception as e:
            # Thử fallback: đọc không chỉ định format
            try:
                if not os.path.exists(audio_path):
                    print(f"[AI-LỖI] _transcribe_audio (fallback): File không tồn tại: {audio_path}")
                    return ""
                sound = AudioSegment.from_file(audio_path)
                sound = sound.set_frame_rate(16000).set_channels(1)
                sound.export(wav_path, format="wav")
                if not os.path.exists(wav_path):
                    print(f"[AI-LỖI] _transcribe_audio (fallback): Không thể tạo file WAV: {wav_path}")
                    return ""
                speech, rate = librosa.load(wav_path, sr=16000)
                input_values = self.processor(
                    speech, sampling_rate=16000, return_tensors="pt"
                ).input_values
                with torch.no_grad():
                    logits = self.model(input_values.to(self.device)).logits
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.processor.decode(predicted_ids[0])
                return transcription.lower()
            except Exception as e2:
                print(f"[AI-LỖI] _transcribe_audio: {e2}")
                import traceback
                print(f"[AI-LỖI] Traceback: {traceback.format_exc()}")
                return ""
        finally:
            # Xóa file WAV tạm nếu tồn tại và không phải file gốc
            if os.path.exists(wav_path) and wav_path != audio_path:
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

    def get_assessment(self, audio_path, target_word):
        target_phonemes = [
            re.sub(r"[0-9]", "", ph)
            for ph in self.g2p(target_word)
            if ph.strip() and ph not in (",", ".")
        ]
        transcribed_text = self._transcribe_audio(audio_path)
        if not transcribed_text.strip():
            results = [
                {"phoneme": ph, "score": 0, "correct": False} for ph in target_phonemes
            ]
            return results, 0
        transcribed_phonemes = [
            re.sub(r"[0-9]", "", ph)
            for ph in self.g2p(transcribed_text)
            if ph.strip() and ph not in (",", ".")
        ]
        results = []
        score_sum = 0
        s = difflib.SequenceMatcher(None, target_phonemes, transcribed_phonemes)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == "equal":
                for ph in target_phonemes[i1:i2]:
                    results.append({"phoneme": ph, "score": 100, "correct": True})
                    score_sum += 100
            elif tag == "replace":
                for ph in target_phonemes[i1:i2]:
                    results.append({"phoneme": ph, "score": 30, "correct": False})
                    score_sum += 30
            elif tag == "delete":
                for ph in target_phonemes[i1:i2]:
                    results.append({"phoneme": ph, "score": 10, "correct": False})
                    score_sum += 10
        if not results:
            results = [
                {"phoneme": ph, "score": 0, "correct": False} for ph in target_phonemes
            ]
            return results, 0
        overall_score = score_sum / len(results)
        return results, overall_score
