import React from "react";
import { ChevronLeft, ChevronRight, Flame } from "lucide-react";
import styles from "./StreakCalendar.module.css";

const WEEKDAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];

// Helper function: Lấy today theo GMT+7 (múi giờ Việt Nam)
const getTodayInGMT7 = () => {
  const now = new Date();
  // Chuyển sang GMT+7 (7 giờ = 7 * 60 * 60 * 1000 ms)
  const gmt7Time = new Date(now.getTime() + (7 * 60 * 60 * 1000));
  // Lấy UTC date (sau khi đã shift sang GMT+7)
  const utcYear = gmt7Time.getUTCFullYear();
  const utcMonth = String(gmt7Time.getUTCMonth() + 1).padStart(2, "0");
  const utcDate = String(gmt7Time.getUTCDate()).padStart(2, "0");
  return `${utcYear}-${utcMonth}-${utcDate}`;
};

const StreakCalendar = ({
  data,
  month,
  isLoading,
  error,
  onPrevMonth,
  onNextMonth,
}) => {
  // Ưu tiên dùng today từ backend, nếu không có thì tính theo GMT+7
  const today = data?.today || getTodayInGMT7();
  const year = month?.year;
  const monthIndex = (month?.month || 1) - 1;
  const firstDay = new Date(year, monthIndex, 1);
  const monthLabel = firstDay.toLocaleDateString("vi-VN", {
    month: "long",
    year: "numeric",
  });
  const leadingBlank = ((firstDay.getDay() + 6) % 7) || 0;
  const days = data?.calendar?.days ?? [];

  const normalizedDays = days.map((day) => {
    const [dYear, dMonth, dDate] = day.date.split("-").map(Number);
    const jsDate = new Date(dYear, dMonth - 1, dDate);
    return {
      ...day,
      label: dDate,
      isToday: day.date === today,
      weekday: jsDate.getDay(),
    };
  });

  const dayCells = [
    ...Array.from({ length: leadingBlank }, (_, idx) => ({
      key: `empty-${idx}`,
      isPlaceholder: true,
    })),
    ...normalizedDays.map((day) => ({
      key: day.date,
      ...day,
    })),
  ];

  const renderCalendar = () => {
    if (error) {
      return <div className={styles.errorState}>{error}</div>;
    }

    if (isLoading && dayCells.length === 0) {
      return (
        <div className={styles.loadingState}>Đang tải lịch streak...</div>
      );
    }

    if (!isLoading && days.length === 0) {
      return (
        <div className={styles.emptyState}>
          Chưa có dữ liệu streak cho tháng này
        </div>
      );
    }

    return (
      <>
        <div className={styles.weekdays}>
          {WEEKDAYS.map((day) => (
            <span key={day}>{day}</span>
          ))}
        </div>
        <div className={styles.grid}>
          {dayCells.map((cell) =>
            cell.isPlaceholder ? (
              <div key={cell.key} className={styles.placeholder} />
            ) : (
              <div
                key={cell.key}
                className={[
                  styles.dayCell,
                  cell.active ? styles.active : "",
                  cell.isToday ? styles.today : "",
                ].join(" ")}
              >
                {cell.label}
              </div>
            )
          )}
        </div>
        <div className={styles.legend}>
          <div className={styles.legendItem}>
            <span className={`${styles.legendDot} ${styles.activeDot}`} />
            <span>Đã học</span>
          </div>
          <div className={styles.legendItem}>
            <span className={`${styles.legendDot} ${styles.todayDot}`} />
            <span>Hôm nay</span>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <p className={styles.subtitle}>Chuỗi ngày học</p>
          <h3>{monthLabel}</h3>
        </div>
        <div className={styles.actions}>
          <button
            type="button"
            aria-label="Tháng trước"
            onClick={onPrevMonth}
            disabled={isLoading}
          >
            <ChevronLeft size={16} />
          </button>
          <button
            type="button"
            aria-label="Tháng sau"
            onClick={onNextMonth}
            disabled={isLoading}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      <div className={styles.statsRow}>
        <div className={styles.statItem}>
          <div className={`${styles.iconBox} ${styles.currentIcon}`}>
            <Flame size={16} />
          </div>
          <div>
            <p>Đang duy trì</p>
            <strong>{data?.current_streak ?? "--"} ngày</strong>
          </div>
        </div>
        <div className={styles.statItem}>
          <div className={`${styles.iconBox} ${styles.longestIcon}`}>
            <Flame size={16} />
          </div>
          <div>
            <p>Dài nhất</p>
            <strong>{data?.longest_streak ?? "--"} ngày</strong>
          </div>
        </div>
      </div>

      <div className={styles.calendarWrapper}>{renderCalendar()}</div>
    </div>
  );
};

export default StreakCalendar;

