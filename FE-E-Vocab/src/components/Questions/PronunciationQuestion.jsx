import React, { useState, useEffect, useRef } from "react";
import { FaVolumeUp } from "react-icons/fa";
import styles from "./Questions.module.css";

function PronunciationQuestion({ 
  question, 
  blob, 
  setBlob, 
  assessment = null, 
  showResult = false, 
  disabled = false 
}) {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

  // Tạo và cleanup blob URL
  useEffect(() => {
    if (blob) {
      // Cleanup URL cũ trước khi tạo mới
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      // Tạo URL mới
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      
      // Cleanup khi component unmount hoặc blob thay đổi
      return () => {
        URL.revokeObjectURL(url);
      };
    } else {
      setAudioUrl(null);
    }
  }, [blob]);

  const startRecording = async () => {
    if (disabled) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('Trình duyệt không hỗ trợ ghi âm.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new window.MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunks.current = [];
      mediaRecorder.ondataavailable = e => { 
        if (e.data.size > 0) audioChunks.current.push(e.data); 
      };
      mediaRecorder.onstop = () => {
        const newBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        setBlob(newBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      setRecording(true);
      mediaRecorder.start();
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Không thể truy cập microphone. Vui lòng cho phép truy cập microphone.');
    }
  };
  
  const stopRecording = () => {
    if (disabled) return;
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div style={{textAlign: 'center'}}>
      {question.definition && (
        <div style={{fontSize: 18, color: '#4b5563', marginBottom: 16, fontWeight: 500}}>
          {question.definition}
        </div>
      )}
      {question.pronunciation && (
        <div style={{fontSize: 16, color: '#6b7280', marginBottom: 8, fontStyle: 'italic'}}>
          /{question.pronunciation}/
        </div>
      )}
      {(question.word || question.target_word) && (
        <div style={{fontSize: 22, fontWeight: 'bold', marginBottom: 12, color: '#111'}}>
          {question.word || question.target_word}
        </div>
      )}
      <div style={{color:'#6b7280', fontSize:13, marginBottom:12}}>
        Tránh nơi ồn ào khi làm ghi âm.
      </div>
      <div style={{display:'flex', gap:8, justifyContent:'center', marginBottom:12}}>
        <button 
          onClick={() => question.audio_url && new Audio(question.audio_url).play()} 
          className={styles.submitBtn}
          disabled={disabled}
        >
          <FaVolumeUp size={20} style={{marginRight: 8}} />
          Nghe mẫu
        </button>
        {recording
          ? <button 
              onClick={stopRecording} 
              className={styles.submitBtn} 
              style={{background:'#dc2626', borderColor:'#b91c1c'}} 
              disabled={disabled}
            >
              Dừng ghi âm
            </button>
          : <button 
              onClick={startRecording} 
              className={styles.submitBtn} 
              disabled={disabled}
            >
              Bắt đầu ghi âm
            </button>
        }
      </div>
      {audioUrl && (
        <div style={{marginBottom: 12}}>
          <audio key={audioUrl} controls src={audioUrl} style={{width: 320}} />
          <p style={{fontSize: 12, color: '#666', marginTop: 8}}>Nhấn play để nghe lại ghi âm của bạn</p>
        </div>
      )}
      {!blob && (
        <div style={{color:'#6b7280', fontSize:13}}>
          {showResult 
            ? 'Bấm "Bắt đầu ghi âm", sau đó nhấn "Kiểm tra" để chấm điểm.' 
            : 'Bấm "Bắt đầu ghi âm" để ghi lại giọng của bạn.'}
        </div>
      )}
      {showResult && assessment && (
        <div style={{marginTop: 6, fontSize:12, color:'#64748b'}}>
          Bạn có thể ghi âm lại nếu muốn cải thiện điểm.
        </div>
      )}
    </div>
  );
}

export default PronunciationQuestion;

