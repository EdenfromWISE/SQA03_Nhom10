import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./HeroSection.module.css";
import heroImg from "../assets/open-book.png"; // thay bằng ảnh minh họa của bạn

const HeroSection = () => {
  const navigate = useNavigate();

  // Khi bấm nút => chuyển sang /course
  const handleStart = () => {
    navigate("/course");
  };

  return (
    <section className={styles.hero}>
      <div className={styles.left}>
        <h1 className={styles.title}>
          Học <span className={styles.green}>1000+</span> từ vựng tiếng Anh mới{" "}
          <span className={styles.blue}>dễ dàng hơn</span> mỗi ngày
        </h1>

        <p className={styles.desc}>
          Phương pháp học thông minh với flashcard, theo dõi tiến độ và đánh giá
          phát âm. Biến việc học từ vựng thành thói quen hàng ngày.
        </p>

        <button onClick={handleStart} className={styles.ctaBtn}>
          ▶ Bắt đầu học ngay
        </button>

        <div className={styles.info}>
          <span>🆓 Miễn phí </span>
          <span>👥 50,000+ học viên</span>
          <span>⭐ 4.9/5 đánh giá</span>
        </div>
      </div>

      <div className={styles.right}>
        <img src={heroImg} alt="Học viên vui vẻ" />
      </div>
    </section>
  );
};

export default HeroSection;
