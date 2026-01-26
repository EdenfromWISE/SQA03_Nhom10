import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./UpcomingReview.module.css";
import { Calendar } from "lucide-react";

const UpcomingReview = ({ data, isLoading = false, error = "" }) => {
  const navigate = useNavigate();

  const formatDayOfWeek = (dateString) => {
    // Parse date string (YYYY-MM-DD) theo local time (GMT+7) thay vì UTC
    // Tránh lỗi timezone khi parse date string không có time
    const [year, month, day] = dateString.split("-").map(Number);
    const date = new Date(year, month - 1, day); // Local date, không phụ thuộc timezone
    const days = ["Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];
    return days[date.getDay()];
  };

  const formatWordsPreview = (words, maxLength = 50) => {
    if (!words || words.length === 0) return "";
    
    let preview = words.map(w => w.word).join(", ");
    if (preview.length > maxLength) {
      preview = preview.substring(0, maxLength).trim() + "...";
    }
    return preview;
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <Calendar size={18} className={styles.icon} />
          <h3>Từ vựng sắp ôn tập</h3>
        </div>
        <button 
          className={styles.reviewButton}
          onClick={() => navigate("/review")}
        >
          Ôn tập hôm nay
        </button>
      </div>

      <div className={styles.content}>
        {isLoading ? (
          <div className={styles.emptyState}>
            <span>Đang tải...</span>
          </div>
        ) : error ? (
          <div className={styles.emptyState}>
            <span>{error}</span>
          </div>
        ) : data && data.length > 0 ? (
          data.map((dayData, index) => (
            <div key={index} className={styles.dayRow}>
              <div className={styles.dayInfo}>
                <span className={styles.dayOfWeek}>{formatDayOfWeek(dayData.date)}</span>
                <span className={styles.count}>{dayData.count} từ</span>
              </div>
              <div className={styles.wordsPreview}>
                {formatWordsPreview(dayData.words)}
              </div>
            </div>
          ))
        ) : (
          <div className={styles.emptyState}>
            <span>Không có từ vựng cần ôn tập</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default UpcomingReview;

