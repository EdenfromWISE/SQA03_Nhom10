// FeedbackSection.jsx
import React from 'react';
import styles from './FeedbackSection.module.css';
import avatar1 from '../assets/avatar1.png';
import avatar2 from '../assets/avatar2.png';
import avatar3 from '../assets/avatar3.png';
import avatar4 from '../assets/avatar4.png';

// 📢 Phần phản hồi học viên (4 khung)
function FeedbackSection() {
  const feedbacks = [
    {
      name: 'Ngọc Lan',
      comment:
        'Ứng dụng giúp mình học từ vựng dễ nhớ hơn rất nhiều. Flashcard gọn gàng và có đánh giá phát âm cực hay!',
      rating: 5,
      avatar: avatar1,
    },
    {
      name: 'Minh Tấn',
      comment:
        'Tính năng theo dõi tiến độ giúp mình duy trì thói quen học mỗi ngày. Giao diện thân thiện và dễ dùng.',
      rating: 5,
      avatar: avatar2,
    },
    {
      name: 'Thu Hà',
      comment:
        'Phần đánh giá phát âm rất chính xác, giúp mình tự tin nói tiếng Anh hơn hẳn!',
      rating: 4,
      avatar: avatar3,
    },
    {
      name: 'Quốc Bảo',
      comment:
        'Rất hữu ích! Mỗi ngày mình học 20 từ mới mà không cảm thấy nhàm chán. Rất đáng thử!',
      rating: 5,
      avatar: avatar4,
    },
  ];

  return (
    <section className={styles.feedback}>
      <h2>Phản hồi từ học viên</h2>
      <p>Hàng ngàn học viên đã cải thiện khả năng tiếng Anh với VocabMaster</p>

      <div className={styles.grid}>
        {feedbacks.map((f, i) => (
          <div key={i} className={styles.card}>
            <img src={f.avatar} alt={f.name} className={styles.avatar} />
            <h3>{f.name}</h3>
            <p className={styles.comment}>“{f.comment}”</p>
            <div className={styles.stars}>
              {'⭐'.repeat(f.rating)}
              {'☆'.repeat(5 - f.rating)}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default FeedbackSection;
