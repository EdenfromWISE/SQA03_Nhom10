// VocabularyListPage.jsx
import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import styles from "./VocabularyListPage.module.css"; // CSS Modules
import { FaVolumeUp } from "react-icons/fa";
import { env } from "../config/env";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

function VocabularyListPage() {
  useDocumentTitle("Danh sách từ vựng");
  const [topic, setTopic] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isStartingExam, setIsStartingExam] = useState(false);
  const [flipped, setFlipped] = useState(false);

  const { topicId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      const token =
        localStorage.getItem("accessToken") || sessionStorage.getItem("accessToken");
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
        console.error("Error fetching topic details", err);
        navigate("/");
      }
    };
    fetchData();
  }, [topicId, navigate]);

  if (!topic) return <div className={styles.topicPage}>Đang tải...</div>;

  const vocabularies = topic.vocabularies || [];
  const currentVocab = vocabularies[currentIndex] || null;

  const handleNext = () => {
    setFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % vocabularies.length);
  };

  const handlePrev = () => {
    setFlipped(false);
    setCurrentIndex((prev) =>
      prev === 0 ? vocabularies.length - 1 : prev - 1
    );
  };

  const handleStartExam = async (topicId) => {
    if (isStartingExam) return; // Tránh click nhiều lần

    setIsStartingExam(true);
    navigate(`/exam/topic/${topicId}`);

    // Reset sau 2 giây
    setTimeout(() => setIsStartingExam(false), 2000);
  };

  return (
    <div className={styles.topicPage}>
      {/* Main content */}
      <div className={styles.main}>
        <button
          className={styles.backBtn}
          onClick={() => navigate(`/course/${topic.course_id}`)}
        >
          ← Quay lại
        </button>

        {/* Flashcard Zone */}
        {currentVocab && (
          <div className={styles.flashcardZone}>
            <div
              className={`${styles.flashcardHorizontal} ${flipped ? styles.flipped : ""}`}
              onClick={() => setFlipped(!flipped)}
            >
              {/* Front */}
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

              {/* Back */}
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
                <p><em>{currentVocab.example_en}</em></p>
                <p>{currentVocab.example_vi}</p>
              </div>
            </div>

            {/* Prev / Next */}
            <div className={styles.flashcardControls}>
              <button onClick={handlePrev} className={styles.navBtn}>
                Prev Word
              </button>
              <button onClick={handleNext} className={styles.navBtn}>
                Next Word
              </button>
              {/* Mobile buttons - chỉ hiển thị khi sidebar bị ẩn */}
              <button 
                onClick={() => navigate(`/practice/${topic.id}`)}
                className={styles.mobileActionBtn}
              >
                Luyện Tập
              </button>
              <button
                className={`${styles.mobileActionBtn} ${styles.examButton}`}
                onClick={() => handleStartExam(topic.id)}
                disabled={isStartingExam}
              >
                {isStartingExam ? "Đang tải..." : "Làm bài kiểm tra"}
              </button>
            </div>
          </div>
        )}

        {/* Vocabulary List */}
        <h3>Các từ vựng trong chủ đề</h3>
        <div className={styles.vocabList}>
          {vocabularies.map((vocab) => (
            <div key={vocab.id} className={styles.vocabRow}>
              <button
                className={`${styles.audioBtn} ${styles.big}`}
                onClick={() => vocab.audio_url && new Audio(vocab.audio_url).play()}
              >
                <FaVolumeUp size={24} color="#fff" />
              </button>
              <div className={styles.vocabWord}>
                <p>
                  <strong>{vocab.word}</strong>{" "}
                  {vocab.part_of_speech && (
                    <span className={styles.pos}>({vocab.part_of_speech})</span>
                  )}
                </p>
                <p className={styles.phonetic}>{vocab.pronunciation}</p>
              </div>
              <div className={styles.vocabMeaning}>{vocab.meaning}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Sidebar */}
      <div className={styles.sidebar}>
        <h3>{topic.title}</h3>
        <button onClick={() => navigate(`/learn/${topic.id}`)}>
          Flashcard
        </button>
        <button onClick={() => navigate(`/practice/${topic.id}`)}>
          Luyện Tập
        </button>
        <button
          className={styles.examButton}
          onClick={() => handleStartExam(topic.id)}
          disabled={isStartingExam}
        >
          {isStartingExam ? "Đang tải..." : "Làm bài kiểm tra"}
        </button>
      </div>
    </div>
  );
}

export default VocabularyListPage;
