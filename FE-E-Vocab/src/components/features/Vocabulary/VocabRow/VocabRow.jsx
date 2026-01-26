import React from 'react';
import AudioButton from '../../../common/AudioButton';
import styles from './VocabRow.module.css';

function VocabRow({ vocab }) {
  return (
    <div className={styles.vocabRow}>
      <AudioButton audioUrl={vocab.audio_url} size={24} />
      
      <div className={styles.vocabWord}>
        <p className={styles.word}>
          <strong>{vocab.word}</strong>
          {vocab.part_of_speech && (
            <span className={styles.pos}>({vocab.part_of_speech})</span>
          )}
        </p>
        <p className={styles.phonetic}>{vocab.pronunciation}</p>
      </div>
      
      <div className={styles.vocabMeaning}>{vocab.meaning}</div>
    </div>
  );
}

export default VocabRow;

