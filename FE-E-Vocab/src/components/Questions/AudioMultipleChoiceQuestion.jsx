import React from "react";
import { FaVolumeUp } from "react-icons/fa";
import styles from "./Questions.module.css";

function AudioMultipleChoiceQuestion({ 
  question, 
  userAnswer, 
  setUserAnswer, 
  showResult = false, 
  playAudio, 
  onClickSfx 
}) {
  return (
    <div className={styles.questionContent}>
      <div className={styles.audioSection}>
        <button 
          className={styles.audioButton}
          onClick={() => playAudio(question.audio_url)}
          disabled={showResult}
        >
          <FaVolumeUp size={24} />
          Nghe phát âm
        </button>
        <p className={styles.audioInstruction}>
          Nhấn nút trên để nghe từ, sau đó chọn nghĩa đúng
        </p>
      </div>
      
      <div className={styles.options}>
        {question.options.map((option, index) => (
          <button
            key={index}
            className={`${styles.option} ${
              userAnswer === index ? styles.selectedOption : ''
            }`}
            onClick={() => { 
              if (showResult) return; 
              onClickSfx && onClickSfx(); 
              setUserAnswer(index); 
            }}
            disabled={showResult}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

export default AudioMultipleChoiceQuestion;

