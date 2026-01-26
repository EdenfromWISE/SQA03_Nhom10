import React from "react";
import { FaCheck } from "react-icons/fa";
import styles from "./Common.module.css";

function CompletionScreen({ 
  title = "Chúc mừng!", 
  message, 
  stats = null,
  buttonText = "Quay lại",
  onButtonClick 
}) {
  return (
    <div className={styles.completionScreen}>
      <div className={styles.completionContent}>
        <div className={styles.completionIcon}>
          <FaCheck size={64} />
        </div>
        <h1 className={styles.completionTitle}>{title}</h1>
        <p className={styles.completionMessage}>{message}</p>
        {stats && (
          <div className={styles.completionStats}>
            {stats.map((stat, index) => (
              <p key={index}>
                {stat.label}: <strong>{stat.value}</strong>
              </p>
            ))}
          </div>
        )}
        <button 
          className={styles.completionButton}
          onClick={onButtonClick}
        >
          {buttonText}
        </button>
      </div>
    </div>
  );
}

export default CompletionScreen;

