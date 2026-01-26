import React from 'react';
import { FaVolumeUp } from 'react-icons/fa';
import styles from './AudioButton.module.css';

function AudioButton({ audioUrl, size = 22, className = '' }) {
  const handlePlay = (e) => {
    e.stopPropagation();
    if (audioUrl) {
      new Audio(audioUrl).play();
    }
  };

  if (!audioUrl) return null;

  return (
    <button
      className={`${styles.audioBtn} ${className}`}
      onClick={handlePlay}
      aria-label="Phát âm thanh"
    >
      <FaVolumeUp size={size} color="#fff" />
    </button>
  );
}

export default AudioButton;

