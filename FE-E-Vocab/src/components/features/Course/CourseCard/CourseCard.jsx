import React from 'react';
import { Link } from 'react-router-dom';
import styles from './CourseCard.module.css';
import PLACEHOLDER_IMG from '../../../../assets/placeholder.png';

function CourseCard({ course, onToggleFavorite }) {
  return (
    <div className={styles.courseCard}>
      <Link to={`/course/${course.id}`} className={styles.courseLink}>
        <div className={styles.courseThumb}>
          <img
            src={course.image_url || PLACEHOLDER_IMG}
            alt={course.title}
            className={styles.courseImg}
          />
        </div>

        <div className={styles.cardBody}>
          <div className={styles.courseTitle}>{course.title}</div>
          <div className={styles.courseMeta}>
            {Array.isArray(course.topics) ? course.topics.length : 0} chủ đề
          </div>
        </div>
      </Link>

      <div className={styles.cardFooter}>
        <button
          className={`${styles.favoriteBtn} ${course.is_favorite ? styles.active : ''}`}
          onClick={() => onToggleFavorite?.(course.id)}
          aria-label={course.is_favorite ? 'Bỏ yêu thích' : 'Thêm yêu thích'}
        >
          <svg viewBox="0 0 24 24" className={styles.heartIcon}>
            <path d="M12 21s-6.1-4.4-9.5-8.2C-1.5 8.1 2.2 2 7.5 3.5 10 4.3 12 6.6 12 6.6s2-2.3 4.5-3.1C21.8 2 25.5 8.1 21.5 12.8 18.1 16.6 12 21 12 21z" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default CourseCard;

