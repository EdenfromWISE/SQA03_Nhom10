"""
Question type: Speaking - Phát âm từ tiếng Anh tương ứng với nghĩa.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from django.apps import apps
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile

from vocabulary.models import Vocabulary
from .base import QuestionTypeBase


class SpeakingQuestionType(QuestionTypeBase):
    """Câu hỏi phát âm từ tiếng Anh tương ứng với nghĩa."""
    
    QUESTION_TYPE = "speaking"
    DISPLAY_NAME = "Phát âm từ tiếng Anh"
    
    @classmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo câu hỏi speaking: phát âm từ tiếng Anh tương ứng với nghĩa.
        
        Args:
            vocabulary: Từ vựng chính
            pool: Không sử dụng trong speaking (có thể None)
        """
        question_data = {
            "id": f"speaking_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Phát âm từ tiếng Anh tương ứng với nghĩa",
            "prompt": {
                "definition": vocabulary.meaning,
                "word": vocabulary.word,
                "target_word": vocabulary.word,  # Giữ lại để tương thích
                "pronunciation": vocabulary.pronunciation or "",
                "audio_url": vocabulary.audio_url or "",
            },
            "answer": vocabulary.word.lower().strip(),
            "explanation": f"'{vocabulary.meaning}' có nghĩa là '{vocabulary.word}'",
            "metadata": {"vocabulary_id": vocabulary.id},
        }
        
        if not cls.validate_question_data(question_data):
            raise ValueError(f"Dữ liệu câu hỏi không hợp lệ: {question_data}")
        
        return question_data
    
    @classmethod
    def evaluate_answer(
        cls,
        user_answer: Any,
        question: Dict[str, Any],
        pronunciation_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Đánh giá câu trả lời speaking.
        
        Args:
            user_answer: Có thể là:
                - UploadedFile: File audio từ người dùng
                - float: Điểm pronunciation_score đã được tính sẵn
                - Dict: Dict chứa pronunciation_score hoặc audio_file
            question: Câu hỏi đã được tạo
            pronunciation_score: Điểm phát âm (nếu đã được tính sẵn)
        """
        target_word = question.get("answer", "").lower().strip()
        
        # Lấy pronunciation_assessor từ learning app
        learning_app = apps.get_app_config('learning')
        assessor = learning_app.pronunciation_assessor
        
        if assessor is None:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Hệ thống đánh giá phát âm chưa sẵn sàng.",
            }
        
        # Xử lý user_answer: có thể là file, float, hoặc dict
        final_pronunciation_score = pronunciation_score
        phoneme_results = None
        
        # Trường hợp 1: user_answer là UploadedFile
        if isinstance(user_answer, UploadedFile):
            final_pronunciation_score, phoneme_results = cls._process_audio_file(
                user_answer, target_word, assessor
            )
            if final_pronunciation_score is None:
                return {
                    "is_correct": False,
                    "score": 0.0,
                    "feedback": "Lỗi khi xử lý file audio.",
                }
        
        # Trường hợp 2: user_answer là float (pronunciation_score đã được tính)
        elif isinstance(user_answer, (int, float)):
            final_pronunciation_score = float(user_answer)
            phoneme_results = []
        
        # Trường hợp 3: user_answer là dict chứa pronunciation_score hoặc audio_file
        elif isinstance(user_answer, dict):
            if "pronunciation_score" in user_answer:
                final_pronunciation_score = float(user_answer["pronunciation_score"])
                phoneme_results = user_answer.get("phonemes", [])
            elif "audio_file" in user_answer:
                audio_file = user_answer["audio_file"]
                final_pronunciation_score, phoneme_results = cls._process_audio_file(
                    audio_file, target_word, assessor
                )
                if final_pronunciation_score is None:
                    return {
                        "is_correct": False,
                        "score": 0.0,
                        "feedback": "Lỗi khi xử lý file audio.",
                    }
            else:
                return {
                    "is_correct": False,
                    "score": 0.0,
                    "feedback": "Định dạng câu trả lời không hợp lệ.",
                }
        
        else:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Câu trả lời phải là file audio hoặc điểm phát âm.",
            }
        
        # Xác định điểm số và phản hồi
        if final_pronunciation_score is None:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Không thể đánh giá phát âm.",
            }
        
        # Chuyển đổi điểm từ 0-100 sang 0-1
        normalized_score = final_pronunciation_score / 100.0
        
        # Coi như đúng nếu điểm >= 70
        is_correct = final_pronunciation_score >= 70.0
        
        # Tạo feedback dựa trên điểm số
        feedback = cls._get_feedback(final_pronunciation_score)
        
        result = {
            "is_correct": is_correct,
            "score": normalized_score,
            "feedback": feedback,
            "pronunciation_score": final_pronunciation_score,
        }
        
        # Thêm chi tiết phonemes nếu có
        if phoneme_results:
            result["phonemes"] = phoneme_results
        
        return result
    
    @classmethod
    def requires_pool(cls) -> bool:
        """Speaking không cần pool để tạo phương án nhiễu."""
        return False
    
    @classmethod
    def _process_audio_file(cls, audio_file: UploadedFile, target_word: str, assessor) -> tuple[Optional[float], Optional[List]]:
        """
        Xử lý file audio và trả về điểm phát âm.
        
        Returns:
            Tuple (pronunciation_score, phoneme_results) hoặc (None, None) nếu lỗi
        """
        audio_path = None
        try:
            # Lưu file tạm
            fs = FileSystemStorage()
            filename = fs.save(audio_file.name, audio_file)
            audio_path = fs.path(filename)
            
            # Kiểm tra file đã được lưu thành công
            if not os.path.exists(audio_path):
                print(f"[Speaking] Lỗi: File không tồn tại sau khi lưu: {audio_path}")
                return None, None
            
            # Đánh giá phát âm
            phoneme_results, pronunciation_score = assessor.get_assessment(
                audio_path, target_word
            )
            return pronunciation_score, phoneme_results
        except Exception as e:
            import traceback
            print(f"[Speaking] Lỗi xử lý audio: {e}")
            print(f"[Speaking] Traceback: {traceback.format_exc()}")
            return None, None
        finally:
            # Xóa file tạm sau khi xử lý xong
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    print(f"[Speaking] Warning: Không thể xóa file tạm {audio_path}: {e}")
    
    @classmethod
    def _get_feedback(cls, score: float) -> str:
        """Tạo feedback dựa trên điểm số phát âm."""
        if score >= 90:
            return "Phát âm xuất sắc!"
        elif score >= 80:
            return "Phát âm rất tốt!"
        elif score >= 70:
            return "Phát âm khá tốt, cần luyện tập thêm."
        elif score >= 50:
            return "Phát âm cần cải thiện. Hãy nghe lại và thử lại."
        else:
            return "Phát âm chưa chính xác. Hãy luyện tập thêm."


# Giữ lại các hàm cũ để tương thích ngược (deprecated)
QUESTION_TYPE = SpeakingQuestionType.QUESTION_TYPE


def build_question(vocabulary: Vocabulary) -> Dict[str, Any]:
    """Deprecated: Sử dụng SpeakingQuestionType.build_question thay thế."""
    return SpeakingQuestionType.build_question(vocabulary)


def evaluate_answer(user_answer: Any, question: Dict[str, Any]) -> Dict[str, Any]:
    """Deprecated: Sử dụng SpeakingQuestionType.evaluate_answer thay thế."""
    return SpeakingQuestionType.evaluate_answer(user_answer, question)
