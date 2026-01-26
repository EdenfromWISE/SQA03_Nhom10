// LearnFlashcardPage.jsx
import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import styles from "./LearnFlashcardPage.module.css";
import { FaVolumeUp, FaHeart, FaRegHeart } from "react-icons/fa";
import { env } from "../config/env";
import { useDocumentTitle } from '../hooks/useDocumentTitle';

function LearnFlashcardPage() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  
  const [topic, setTopic] = useState(null);
  useDocumentTitle(topic ? `Học Flashcard - ${topic.title}` : 'Học Flashcard');

  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [favorites, setFavorites] = useState([]);

  // ------------------------------------------------------
  // Lấy dữ liệu chủ đề + từ vựng
  // ------------------------------------------------------
  useEffect(() => {
    const fetchTopic = async () => {
      const token =
        localStorage.getItem("accessToken") || sessionStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }
      try {
        const res = await axios.get(env.API_ENDPOINTS.VOCABULARY.TOPIC_VOCABULARY(topicId), {
          headers: { Authorization: `Bearer ${token}` },
        });
        setTopic(res.data);
      } catch (err) {
        console.error("Lỗi khi tải dữ liệu:", err);
      }
    };
    fetchTopic();
  }, [topicId, navigate]);

  if (!topic) return <div className={styles.loading}>Đang tải...</div>;

  const vocabularies = topic.vocabularies || [];
  const currentVocab = vocabularies[currentIndex];

  // ------------------------------------------------------
  // Xử lý chuyển từ
  // ------------------------------------------------------
  const handleNext = () => {
    setFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % vocabularies.length);
  };

  const handlePrev = () => {
    setFlipped(false);
    setCurrentIndex((prev) => (prev === 0 ? vocabularies.length - 1 : prev - 1));
  };

  // ------------------------------------------------------
  // Xử lý yêu thích
  // ------------------------------------------------------
  const toggleFavorite = (vocabId) => {
    setFavorites((prev) =>
      prev.includes(vocabId) ? prev.filter((id) => id !== vocabId) : [...prev, vocabId]
    );
  };

  // ------------------------------------------------------
  // Giao diện chính
  // ------------------------------------------------------
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <Link to={`/topic/${topicId}`} className={styles.backBtn}>
          ← Quay lại
        </Link>
        <div className={styles.headerContent}>
          <h2>{topic.title}</h2>
          <div className={styles.headerCounter}>
            <strong>{currentIndex + 1}</strong> / {vocabularies.length}
          </div>
        </div>
      </div>

      {/* Flashcard */}
      <div className={styles.flashcardZone}>
        <div
          className={`${styles.flashcardHorizontal} ${flipped ? styles.flipped : ""}`}
          onClick={() => setFlipped(!flipped)}
        >
          {/* Mặt trước */}
          <div className={`${styles.flashcardFace} ${styles.front}`}>
            <div className={styles.flashcardLeft}>
              {currentVocab.image_url && (
                <img
                  src={currentVocab.image_url}
                  alt={currentVocab.word}
                  className={styles.flashcardImage}
                />
              )}
            </div>
            <div className={styles.flashcardRight}>
              <div className={styles.progress}>
                {currentIndex + 1}/{vocabularies.length}
              </div>
              <h2 className={styles.flashcardWord}>{currentVocab.word}</h2>
              {currentVocab.audio_url && (
                <button
                  className={styles.audioBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    new Audio(currentVocab.audio_url).play();
                  }}
                >
                  <FaVolumeUp size={22} color="#fff" />
                </button>
              )}
            </div>
          </div>

          {/* Mặt sau */}
          <div className={`${styles.flashcardFace} ${styles.back}`}>
            <div className={styles.pronunciationSection}>
              <p><strong>{currentVocab.pronunciation}</strong></p>
              {currentVocab.audio_url && (
                <button
                  className={styles.audioBtnBack}
                  onClick={(e) => {
                    e.stopPropagation();
                    new Audio(currentVocab.audio_url).play();
                  }}
                >
                  <FaVolumeUp size={18} color="#fff" />
                </button>
              )}
            </div>
            <p>{currentVocab.meaning}</p>
            {currentVocab.example_en && (
              <p><em>{currentVocab.example_en}</em></p>
            )}
            {currentVocab.example_vi && (
              <p>{currentVocab.example_vi}</p>
            )}
          </div>
        </div>
      </div>

      {/* Nút điều hướng */}
      <div className={styles.controls}>
        <button onClick={handlePrev} className={styles.navBtn}>← Trước</button>
        <button onClick={handleNext} className={styles.navBtn}>Sau →</button>
      </div>

      {/* Nút yêu thích */}
      <div className={styles.favoriteZone}>
        <button
          className={styles.favoriteBtn}
          onClick={() => toggleFavorite(currentVocab.id)}
        >
          {favorites.includes(currentVocab.id) ? (
            <>
              <FaHeart color="red" size={18} /> Đã yêu thích
            </>
          ) : (
            <>
              <FaRegHeart size={18} /> Thêm vào yêu thích
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default LearnFlashcardPage;
