import React from "react";
import { FaCheck, FaTimes } from "react-icons/fa";
import { mapArpabetToIpa } from "../../utils/pronunciation";
import styles from "./Common.module.css";

function ResultDisplay({ 
  isCorrect, 
  feedback, 
  questionType, 
  pronunciationAssessment = null 
}) {
  if (questionType === 'pronunciation' && pronunciationAssessment) {
    return (
      <div
        className={`${styles.result} ${isCorrect ? styles.correct : styles.incorrect}`}
        style={{ textAlign: "center" }}
      >
        <div className={styles.resultText}>
          <h3 style={{ marginBottom: 8 }}>{isCorrect ? "Tuyệt vời!" : "Rất tiếc!"}</h3>
          <p style={{ marginTop: -4, marginBottom: 8 }}>{feedback}</p>
          <p>
            Điểm phát âm:{" "}
            <strong>
              {pronunciationAssessment?.score ? pronunciationAssessment.score.toFixed(1) : 0}/100
            </strong>{" "}
            {isCorrect ? "(Đạt)" : "(Chưa đạt)"}
          </p>
          {Array.isArray(pronunciationAssessment?.phonemes) && (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: 8,
                justifyContent: "center",
                marginTop: 10,
              }}
            >
              {pronunciationAssessment.phonemes.map((p, i) => (
                <span
                  key={i}
                  style={{
                    background: p.correct ? "#dcfce7" : "#fee2e2",
                    border: `1px solid ${p.correct ? "#22c55e" : "#ef4444"}`,
                    color: "#111",
                    padding: "4px 8px",
                    borderRadius: 8,
                    fontWeight: 600,
                  }}
                >
                  {mapArpabetToIpa(p.phoneme)}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.result} ${isCorrect ? styles.correct : styles.incorrect}`}>
      <div className={styles.resultIcon}>
        {isCorrect ? <FaCheck /> : <FaTimes />}
      </div>
      <div className={styles.resultText}>
        <h3>{isCorrect ? "Tuyệt vời!" : "Rất tiếc!"}</h3>
        <p>{feedback}</p>
      </div>
    </div>
  );
}

export default ResultDisplay;

