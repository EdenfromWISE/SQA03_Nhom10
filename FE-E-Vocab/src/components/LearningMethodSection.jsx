// LearningMethodSection.jsx
import React from 'react';
import styles from './LearningMethodSection.module.css';
import methodImg from '../assets/spaced_repetition.png'; // bạn có thể thay bằng ảnh minh họa thật

function LearningMethodSection() {
  return (
    <section className={styles.methodSection}>
      <div className={styles.container}>
        {/* Bên trái: nội dung giới thiệu */}
        <div className={styles.textBox}>
          <h2>Phương pháp học ngắt quãng (Spaced Repetition)</h2>
          <p>
            <strong>Spaced Repetition</strong> là kỹ thuật học giúp bạn ghi nhớ từ vựng lâu hơn
            bằng cách <span className={styles.highlight}>ôn tập lại vào thời điểm mà bạn sắp quên</span>.
            Ứng dụng sẽ tự động gợi ý từ cần ôn dựa trên lịch sử học của bạn.
          </p>
          <ul>
            <li>⏳ Ôn lại vào đúng thời điểm “vàng” giúp nhớ lâu hơn gấp nhiều lần.</li>
            <li>🧠 Tập trung vào những từ khó, giảm thời gian lặp lại từ đã quen.</li>
            <li>📈 Tiến bộ rõ rệt sau chỉ vài ngày luyện tập.</li>
          </ul>          
        </div>

        {/* Bên phải: ảnh minh họa */}
        <div className={styles.imageBox}>
          <img src={methodImg} alt="Spaced Repetition" />
        </div>
      </div>
    </section>
  );
}

export default LearningMethodSection;
