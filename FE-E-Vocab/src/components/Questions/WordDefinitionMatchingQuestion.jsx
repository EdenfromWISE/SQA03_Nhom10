import React, { useState } from "react";
import styles from "./Questions.module.css";

function WordDefinitionMatchingQuestion({ 
  question, 
  selectedOptions, 
  setSelectedOptions, 
  showResult = false, 
  onClickSfx 
}) {
  const [selectedWord, setSelectedWord] = useState(null);
  const [selectedDefinition, setSelectedDefinition] = useState(null);

  const handleWordClick = (word) => {
    if (showResult) return;
    onClickSfx && onClickSfx();
    if (selectedOptions.some(pair => pair.word === word)) {
      setSelectedOptions(selectedOptions.filter(pair => pair.word !== word));
      return;
    }
    if (selectedWord === word) {
      setSelectedWord(null);
    } else {
      setSelectedWord(word);
    }
  };

  const handleDefinitionClick = (definition) => {
    if (showResult) return;
    onClickSfx && onClickSfx();
    if (selectedOptions.some(pair => pair.definition === definition)) {
      setSelectedOptions(selectedOptions.filter(pair => pair.definition !== definition));
      return;
    }
    if (selectedDefinition === definition) {
      setSelectedDefinition(null);
    } else if (selectedWord) {
      const newPair = { word: selectedWord, definition };
      setSelectedOptions([...selectedOptions, newPair]);
      setSelectedWord(null);
      setSelectedDefinition(null);
    } else {
      setSelectedDefinition(definition);
    }
  };

  const isWordSelected = (word) => selectedOptions.some(pair => pair.word === word);
  const isDefinitionSelected = (definition) => selectedOptions.some(pair => pair.definition === definition);

  return (
    <div className={styles.questionContent}>
      <div className={styles.matchingContainer}>
        <div className={styles.wordsColumn}>
          {question.words.map((word, index) => {
            const isMatched = isWordSelected(word);
            return (
              <button
                key={index}
                className={`${styles.matchingItem} ${
                  selectedWord === word ? styles.selectedMatchingItem : ''
                } ${isMatched ? styles.matchedItem : ''}`}
                onClick={() => handleWordClick(word)}
                disabled={showResult}
              >
                {word}
              </button>
            );
          })}
        </div>
        <div className={styles.definitionsColumn}>
          {question.definitions.map((definition, index) => {
            const isMatched = isDefinitionSelected(definition);
            return (
              <button
                key={index}
                className={`${styles.matchingItem} ${
                  selectedDefinition === definition ? styles.selectedMatchingItem : ''
                } ${isMatched ? styles.matchedItem : ''}`}
                onClick={() => handleDefinitionClick(definition)}
                disabled={showResult}
              >
                {definition}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default WordDefinitionMatchingQuestion;

