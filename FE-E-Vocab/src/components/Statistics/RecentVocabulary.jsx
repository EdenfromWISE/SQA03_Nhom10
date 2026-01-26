import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./RecentVocabulary.module.css";

const RecentVocabulary = ({ data }) => {
  const navigate = useNavigate();

  const handleRowClick = (sessionId) => {
    if (sessionId) {
      navigate(`/session/${sessionId}`);
    }
  };

  return (
    <div className={styles.container}>
      <h3>Các phiên học gần đây</h3>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Thời gian</th>
            <th>Loại</th>
            <th>Số từ</th>
            <th>Kết quả</th>
            <th>Trạng thái</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, i) => (
            <tr
              key={i}
              className={item.id ? styles.clickableRow : ''}
              onClick={() => item.id && handleRowClick(item.id)}
              style={{ cursor: item.id ? 'pointer' : 'default' }}
            >
              <td>
                <span className={styles.word}>{item.time || item.learnedAt}</span>
              </td>
              <td>{item.type || "Học từ vựng"}</td>
              <td>{item.wordsCount || 0} từ</td>
              <td>
                <div className={styles.confidenceBar}>
                  <div
                    className={styles.barFill}
                    style={{
                      width: `${item.result ? parseInt(item.result.replace('%', '')) : 0}%`
                    }}
                  ></div>
                </div>
                <span className={styles.confText}>{item.result || "0%"}</span>
              </td>
              <td className={styles.statusCell}>
                <span className={
                  item.status === "Hoàn thành"
                    ? styles.statusDone
                    : styles.statusLearning
                }
                >
                  {item.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RecentVocabulary;
