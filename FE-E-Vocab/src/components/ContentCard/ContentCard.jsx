import React from 'react';
import { Link } from 'react-router-dom';
import styles from './ContentCard.module.css';

/**
 * ContentCard - Component dùng chung cho Course và Topic cards
 * 
 * @param {Object} props
 * @param {string} props.to - Link đích khi click
 * @param {string} props.imageUrl - URL ảnh (nếu có sẽ làm background)
 * @param {string} props.title - Tiêu đề
 * @param {string} props.meta - Thông tin phụ (vd: "5 chủ đề", "10 từ vựng")
 * @param {boolean} props.isFavorite - Trạng thái yêu thích
 * @param {function} props.onFavoriteClick - Callback khi click favorite
 * @param {boolean} props.showFavorite - Hiển thị nút favorite hay không
 * @param {string} props.progressStatus - Trạng thái tiến độ: "not_started", "in_progress", "completed"
 */
function ContentCard({
  to,
  imageUrl,
  title,
  meta,
  isFavorite = false,
  onFavoriteClick,
  showFavorite = false,
  progressStatus = null,
}) {
  return (
    <Link to={to} className={styles.card}>
      {/* Background layer */}
      <div className={styles.bgLayer}>
        {imageUrl && <img src={imageUrl} alt="" className={styles.bgImage} />}
        <div className={styles.gradient} />
      </div>

      {/* Content */}
      <div className={styles.content}>
        {/* Progress Badge - Top Left */}
        {progressStatus && progressStatus !== "not_started" && (
          <span className={`${styles.progressBadge} ${styles[progressStatus]}`}>
            {progressStatus === "completed" && "✓ Hoàn thành"}
            {progressStatus === "in_progress" && "Đang học"}
          </span>
        )}

        <div className={styles.textArea}>
          <h3 className={styles.title}>{title}</h3>
          <span className={styles.meta}>{meta}</span>
        </div>

        {/* Favorite Button */}
        {showFavorite && (
          <button
            className={`${styles.favoriteBtn} ${isFavorite ? styles.active : ""}`}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onFavoriteClick?.();
            }}
          >
            <svg viewBox="0 0 24 24" className={styles.heartIcon}>
              <path d="M12 21s-6.1-4.4-9.5-8.2C-1.5 8.1 2.2 2 7.5 3.5 10 4.3 12 6.6 12 6.6s2-2.3 4.5-3.1C21.8 2 25.5 8.1 21.5 12.8 18.1 16.6 12 21 12 21z" />
            </svg>
          </button>
        )}
      </div>
    </Link>
  );
}

export default ContentCard;
