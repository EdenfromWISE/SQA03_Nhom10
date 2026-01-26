import React, { useState } from "react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
} from "chart.js";
import styles from "./CourseProgressChart.module.css";

ChartJS.register(ArcElement, Tooltip);

const CourseProgressChart = ({ courses }) => {
  const [showAll, setShowAll] = useState(false);

  const visibleCourses = showAll ? courses : courses.slice(0, 4);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3>Tiến độ học các khóa học</h3>
        {courses.length > 4 && (
          <button
            className={styles.showMoreBtn}
            onClick={() => setShowAll(!showAll)}
          >
            {showAll ? "Ẩn bớt" : "Xem thêm"}
          </button>
        )}
      </div>

      <div className={styles.chartGrid}>
        {visibleCourses.map((course, idx) => {
          const data = {
            datasets: [
              {
                data: [course.progress, 100 - course.progress],
                backgroundColor: [course.color, "#E5E7EB"],
                borderWidth: 0,
              },
            ],
          };

          return (
            <div key={idx} className={styles.chartCard}>
              <div className={styles.chartWrapper}>
                <Doughnut
                  data={data}
                  options={{
                    cutout: "75%",
                    plugins: { tooltip: { enabled: false } },
                  }}
                />
                <div className={styles.centerText}>
                  {course.progress}%
                </div>
              </div>
              <p className={styles.courseName}>{course.name}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CourseProgressChart;
