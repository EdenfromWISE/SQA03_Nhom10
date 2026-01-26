import React from "react";
import styles from "./Questions.module.css";

function DefinitionToWordQuestion({ 
  question, 
  userAnswer, 
  setUserAnswer, 
  showResult = false, 
  onClickSfx 
}) {
  return (
    <div className={styles.questionContent}>
      <p className={styles.definition}>{question.definition}</p>

      {question.example_vi && (
        <p className={styles.example}>
          <strong>Ví dụ:</strong> {question.example_vi}
        </p>
      )}

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

export default DefinitionToWordQuestion;

