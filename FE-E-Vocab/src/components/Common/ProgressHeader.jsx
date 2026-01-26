import React from "react";
import { FaClock } from "react-icons/fa";
import styles from "./Common.module.css";

function ProgressHeader({ 
  onBackClick, 
  backButtonText = "← Quay lại",
  progress = 0,
  showTimer = false,
  timerText = null,
  questionCounter = null
}) {
  return (
    <div className={styles.header}>
      <button 
        className={styles.backBtn}
        onClick={onBackClick}
      >
        {backButtonText}
      </button>
      {showTimer && timerText && (
        <div className={styles.timer}>
          <FaClock className={styles.timerIcon} />
          <span className={styles.timerText}>{timerText}</span>
        </div>
      )}
      <div className={styles.progress}>
        {questionCounter && (
          <div className={styles.questionCounter}>
            {questionCounter}
          </div>
        )}
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export default ProgressHeader;

