import React from "react";
import styles from "./Questions.module.css";

function DefinitionToInputQuestion({ 
  question, 
  userAnswer, 
  setUserAnswer, 
  showResult = false, 
  isCorrect = false,
  onClickSfx 
}) {
  const inputClass = `${styles.answerInput} ${
    showResult ? (isCorrect ? styles.correctInput : styles.incorrectInput) : ''
  }`;
  
  return (
    <div className={styles.questionContent}>
      <p className={styles.definition}>{question.definition}</p>
      {question.example_vi && (
        <p className={styles.example}>
          <strong>Ví dụ:</strong> {question.example_vi}
        </p>
      )}
      {question.hint && (
        <p className={styles.hint}>Gợi ý: {question.hint}</p>
      )}
      <input
        className={inputClass}
        type="text"
        placeholder="Nhập từ..."
        value={userAnswer}
        onChange={(e) => setUserAnswer(e.target.value)}
        disabled={showResult}
      />
    </div>
  );
}

export default DefinitionToInputQuestion;

