import React from "react";
import styles from "./Achievements.module.css";
import { Check, Trophy, Star, Medal, Lock } from "lucide-react";

const iconMap = {
  1: <Medal size={20} color="#fbbf24" />,
  2: <Trophy size={20} color="#22c55e" />,
  3: <Star size={20} color="#3b82f6" />,
  4: <Trophy size={20} color="#9ca3af" />,
};

const Achievements = ({ data }) => {
  return (
    <div className={styles.container}>
      <h3>Huy hiệu thành tích</h3>
      <div className={styles.list}>
        {data.map((item) => {
          const isLocked = item.locked; // thêm field locked: true trong mock data
          return (
            <div
              key={item.id}
              className={`${styles.badge} ${styles[`badge${item.id}`]} ${
                isLocked ? styles.locked : ""
              }`}
            >
              <div className={styles.left}>
                <div className={styles.icon}>{iconMap[item.id]}</div>
                <div>
                  <h4>{item.title}</h4>
                  <p>{item.desc}</p>
                </div>
              </div>
              <div className={styles.right}>
                {isLocked ? (
                  <Lock size={16} color="#d1d5db" strokeWidth={2} />
                ) : (
                  <Check size={18} color="#15803d" strokeWidth={3} />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Achievements;
