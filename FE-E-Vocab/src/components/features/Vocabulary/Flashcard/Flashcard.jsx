import React, { useState } from 'react';
import AudioButton from '../../../common/AudioButton';
import styles from './Flashcard.module.css';

function Flashcard({ vocab, currentIndex, totalCount }) {
  const [flipped, setFlipped] = useState(false);

  const handleFlip = () => setFlipped(!flipped);

  if (!vocab) return null;

  return (
    <div
      className={`${styles.flashcard} ${flipped ? styles.flipped : ''}`}
      onClick={handleFlip}
    >
      {/* Front */}
      <div className={`${styles.face} ${styles.front}`}>
        <div className={styles.left}>
          {vocab.image_url && (
            <img
              src={vocab.image_url}
              alt={vocab.word}
              className={styles.image}
            />
          )}
        </div>
        <div className={styles.right}>
          {totalCount > 0 && (
            <div className={styles.progress}>
              {currentIndex + 1}/{totalCount}
            </div>
          )}
          <h2 className={styles.word}>{vocab.word}</h2>
          <AudioButton audioUrl={vocab.audio_url} />
        </div>
      </div>

      {/* Back */}
      <div className={`${styles.face} ${styles.back}`}>
        <p className={styles.pronunciation}>
          <strong>{vocab.pronunciation}</strong>
        </p>
        <p className={styles.meaning}>{vocab.meaning}</p>
        <p className={styles.example}>
          <em>{vocab.example_en}</em>
        </p>
        <p className={styles.exampleVi}>{vocab.example_vi}</p>
      </div>
    </div>
  );
}

export default Flashcard;

