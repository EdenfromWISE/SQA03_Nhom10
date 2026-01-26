import React from 'react';
import styles from './Loading.module.css';

function Loading({ message = 'Đang tải...', fullScreen = false }) {
  return (
    <div className={`${styles.loading} ${fullScreen ? styles.fullScreen : ''}`}>
      <div className={styles.spinner}></div>
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
}

export default Loading;

