import React from 'react';
import { Link } from 'react-router-dom';
import styles from './TopicCard.module.css';

function TopicCard({ topic }) {
  const vocabCount = topic.word_count ?? 0;

  return (
    <div className={styles.topicCard}>
      <div className={styles.topicThumb}>
        {topic.image_url ? (
          <img src={topic.image_url} alt={topic.title} className={styles.topicImg} />
        ) : (
          <div className={styles.topicPlaceholder}>Không có ảnh</div>
        )}
      </div>

      <div className={styles.topicInfo}>
        <h3 className={styles.topicName}>{topic.title}</h3>
        <p className={styles.vocabCount}>{vocabCount} từ vựng</p>
      </div>

      <Link to={`/topic/${topic.id}`} className={styles.viewBtn}>
        Xem
      </Link>
    </div>
  );
}

export default TopicCard;

