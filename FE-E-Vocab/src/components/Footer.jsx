// Footer.jsx
import React from 'react';
import styles from './Footer.module.css';
import openBookWhite from '../assets/open-book.png';

function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        {/* Cột trái: logo và mô tả */}
        <div className={styles.left}>
          <img src={openBookWhite} alt="VocabMaster Logo" className={styles.logo} />
          <p>Học từ vựng tiếng Anh thông minh, dễ nhớ và hiệu quả hơn mỗi ngày.</p>
        </div>

        {/* Cột giữa: liên kết */}
        <div className={styles.middle}>
          <h4>Liên kết nhanh</h4>
          <ul>
            <li><a href="/course">Khóa học</a></li>
            <li><a href="/login">Đăng nhập</a></li>
            <li><a href="/signup">Đăng ký</a></li>
            <li><a href="/contact">Liên hệ</a></li>
          </ul>
        </div>

        {/* Cột phải: thông tin liên hệ */}
        <div className={styles.right}>
          <h4>Liên hệ</h4>
          <p>Email: support@vocabmaster.com</p>
          <p>Hotline: 0123 456 789</p>
        </div>
      </div>

      <div className={styles.bottom}>
        <p>© 2025 VocabMaster. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
