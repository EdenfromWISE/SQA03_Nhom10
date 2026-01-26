import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './BackButton.module.css';

function BackButton({ to, label = 'Quay lại' }) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (to) {
      navigate(to);
    } else {
      navigate(-1);
    }
  };

  return (
    <button className={styles.backBtn} onClick={handleClick}>
      ← {label}
    </button>
  );
}

export default BackButton;

