// FeatureSection.jsx
import React from 'react';
import styles from './FeatureSection.module.css';

function FeatureSection() {
  const features = [
    {
      title: 'Flashcard thông minh',
      desc: 'Hệ thống lặp lại theo khoảng cách giúp ghi nhớ từ vựng lâu dài và hiệu quả',
      icon: '📚',
      color: '#eef2ff', // nền tím nhạt
    },
    {
      title: 'Theo dõi tiến độ',
      desc: 'Thống kê chi tiết về quá trình học tập, từ đã học và mục tiêu hằng ngày',
      icon: '📈',
      color: '#e8fff4', // nền xanh lá nhạt
    },
    {
      title: 'Đánh giá phát âm',
      desc: 'Công nghệ AI nhận diện giọng nói và phản hồi để cải thiện phát âm',
      icon: '🎤',
      color: '#fff7e6', // nền vàng nhạt
    },
    {
      title: 'Thống kê tiến bộ',
      desc: 'Báo cáo chi tiết về thành tích, streak học tập và so sánh với cộng đồng',
      icon: '🏆',
      color: '#f3e8ff', // nền tím nhạt
    },
  ];

  return (
    <section className={styles.features}>
      <h2>Tính năng nổi bật</h2>
      <p>
        Hệ thống học tập thông minh được thiết kế để tối ưu hóa khả năng ghi nhớ
        và phát triển vốn từ vựng.
      </p>

      <div className={styles.grid}>
        {features.map((item, index) => (
          <div key={index} className={styles.card} style={{ backgroundColor: item.color }}>
            <div className={styles.icon}>{item.icon}</div>
            <h3>{item.title}</h3>
            <p>{item.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default FeatureSection;
