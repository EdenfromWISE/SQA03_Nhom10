import React from "react";
import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
import styles from "./StudyHeatMap.module.css";
// import Tooltip from "react-tooltip";

const StudyHeatMap = ({ data }) => {
  const startDate = new Date(new Date().setDate(new Date().getDate() - 90));
  const endDate = new Date();

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Thời gian học</h3>
      <p className={styles.subtitle}>Hoạt động 3 tháng gần đây</p>

      <div className={styles.heatmapWrapper}>
        <CalendarHeatmap
          startDate={startDate}
          endDate={endDate}
          values={data}
          classForValue={(value) => {
            if (!value) return "color-empty";
            if (value.count >= 60) return "color-scale-4";
            if (value.count >= 40) return "color-scale-3";
            if (value.count >= 20) return "color-scale-2";
            return "color-scale-1";
          }}
          tooltipDataAttrs={(value) => {
            if (!value?.date) return { "data-tip": "Không có dữ liệu" };
            return {
              "data-tip": `${value.date}: ${value.count} phút học`,
            };
          }}
          showWeekdayLabels
        />
        <Tooltip />
      </div>

      <div className={styles.legend}>
        <span>Ít</span>
        <div className={styles.legendColors}>
          <div className="color-scale-1"></div>
          <div className="color-scale-2"></div>
          <div className="color-scale-3"></div>
          <div className="color-scale-4"></div>
        </div>
        <span>Nhiều</span>
      </div>
    </div>
  );
};

export default StudyHeatMap;
