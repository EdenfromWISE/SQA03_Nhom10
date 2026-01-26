import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import styles from "./FlashcardLearnPage.module.css";
import { FaVolumeUp } from "react-icons/fa";
import { env } from "../config/env";

function FlashcardLearnPage() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState(null);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }
      try {
        const res = await axios.get(
          env.API_ENDPOINTS.VOCABULARY.TOPIC_VOCABULARY(topicId),
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setTopic(res.data);
      } catch (err) {
        console.error("Error loading flashcards", err);
        navigate("/");
      }
    };
    fetchData();
  }, [topicId, navigate]);

  if (!topic) return <div>Đang tải Flashcards...</div>;

  const vocabs = topic.vocabularies || [];
  const current = vocabs[index];

  const next = () => {
    setFlipped(false);
    setIndex((prev) => (prev + 1) % vocabs.length);
  };
  const prev = () => {
    setFlipped(false);
    setIndex((prev) => (prev === 0 ? vocabs.length - 1 : prev - 1));
  };

  return (
    <div className={styles.page}>
      <Link to={`/topics/${topicId}`} className={styles.backBtn}>
        ← Quay lại Topic
      </Link>

      {current && (
        <div className={styles.flashcardZone}>
          <div
            className={`${styles.card} ${flipped ? styles.flipped : ""}`}
            onClick={() => setFlipped(!flipped)}
          >
            <div className={`${styles.face} ${styles.front}`}>
              {current.image_url && (
                <img src={current.image_url} alt={current.word} />
              )}
              <h2>{current.word}</h2>
              {current.audio_url && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    new Audio(current.audio_url).play();
                  }}
                >
                  <FaVolumeUp />
                </button>
              )}
            </div>

            <div className={`${styles.face} ${styles.back}`}>
              <p><strong>{current.pronunciation}</strong></p>
              <p>{current.meaning}</p>
              <p><em>{current.example_en}</em></p>
              <p>{current.example_vi}</p>
            </div>
          </div>

          <div className={styles.controls}>
            <button onClick={prev}>Prev</button>
            <span>{index + 1}/{vocabs.length}</span>
            <button onClick={next}>Next</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default FlashcardLearnPage;
