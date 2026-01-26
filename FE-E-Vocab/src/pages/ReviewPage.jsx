import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./PracticePage.module.css";
import {
  createReviewSession,
  getSessionQuestions,
  submitAnswer,
  completeSession,
  assessPronunciation,
} from "../services/learningService";
import { mapQuestions, getBackendType, mapAnswerToBackend } from "../services/questionMapper";
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import useSfx from '../hooks/useSfx';
import {
  AudioMultipleChoiceQuestion,
  DefinitionToWordQuestion,
  DefinitionToInputQuestion,
  WordDefinitionMatchingQuestion,
  PronunciationQuestion
} from '../components/Questions';
import { ResultDisplay, CompletionScreen, ProgressHeader } from '../components/Common';

function ReviewPage() {
  useDocumentTitle('Ôn tập');
  const [sessionId, setSessionId] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [userAnswer, setUserAnswer] = useState("");
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [pronunciationBlob, setPronunciationBlob] = useState(null);
  const [pronunciationAssessment, setPronunciationAssessment] = useState(null);
  const [isAssessingPronunciation, setIsAssessingPronunciation] = useState(false);
  const [skipCounts, setSkipCounts] = useState({});
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());

  const navigate = useNavigate();
  const { playClick, playCorrect, playWrong } = useSfx();

  // Reset phát âm khi đổi câu
  useEffect(() => {
    setPronunciationBlob(null);
    setPronunciationAssessment(null);
    setIsAssessingPronunciation(false);
    setQuestionStartTime(Date.now());
  }, [currentQuestionIndex]);

  const fetchReviewQuestions = useCallback(async () => {
    const token = localStorage.getItem("accessToken") || sessionStorage.getItem("accessToken");
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // 1. Tạo review session
      const sessionResponse = await createReviewSession();
      setSessionId(sessionResponse.session_id);
      setSessionData(sessionResponse);

      // 2. Lấy danh sách câu hỏi
      const questionsResponse = await getSessionQuestions(sessionResponse.session_id);
      const mappedQuestions = mapQuestions(questionsResponse.questions);
      setQuestions(mappedQuestions);
      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching review questions", err);
      setError(err.response?.data?.error || "Hiện tại bạn không có từ nào cần ôn tập.");
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchReviewQuestions();
  }, [fetchReviewQuestions]);

  const currentQuestion = questions[currentQuestionIndex];

  const handleAnswerSubmit = async () => {
    if (!currentQuestion || !sessionId) return;

    const timeSpent = (Date.now() - questionStartTime) / 1000;
    const backendType = getBackendType(currentQuestion.type);

    let answer = userAnswer;
    let pronunciationScore = null;

    switch (currentQuestion.type) {
      case "audio_multiple_choice":
      case "definition_to_word":
        answer = userAnswer;
        break;
      case "definition_to_input":
        answer = userAnswer.trim();
        break;
      case "word_definition_matching":
        answer = mapAnswerToBackend(backendType, selectedOptions);
        break;
      case "pronunciation":
        if (!pronunciationBlob) return;
        try {
          setIsAssessingPronunciation(true);
          const assessment = await assessPronunciation(
            pronunciationBlob,
            currentQuestion.word || currentQuestion.target_word
          );
          setPronunciationAssessment(assessment);
          pronunciationScore = assessment.score;
          answer = pronunciationScore;
        } catch (e) {
          console.error("Pronunciation assess error:", e);
          setFeedback("Lỗi khi đánh giá phát âm");
          setIsCorrect(false);
          setShowResult(true);
          setIsAssessingPronunciation(false);
          playWrong();
          return;
        } finally {
          setIsAssessingPronunciation(false);
        }
        break;
      default:
        break;
    }

    try {
      const result = await submitAnswer(sessionId, currentQuestion.id, answer, timeSpent, pronunciationScore);

      setIsCorrect(result.is_correct);
      setFeedback(result.feedback);
      setShowResult(true);

      if (result.is_correct) playCorrect();
      else playWrong();
    } catch (err) {
      console.error("Error submitting answer", err);
      setError("Có lỗi xảy ra khi gửi câu trả lời");
    }
  };

  const handleSkipPronunciation = () => {
    if (!currentQuestion) return;
    const qid = currentQuestion.id || `q_${currentQuestionIndex}`;
    const count = (skipCounts[qid] || 0) + 1;
    setSkipCounts((prev) => ({ ...prev, [qid]: count }));

    const newQuestions = [...questions];
    const skipped = newQuestions.splice(currentQuestionIndex, 1)[0];

    if (count < 2) {
      newQuestions.push(skipped);
    }

    setQuestions(newQuestions);

    if (newQuestions.length === 0) {
      handleCompleteReview();
      return;
    }
    if (currentQuestionIndex >= newQuestions.length) {
      setCurrentQuestionIndex(0);
    }

    resetQuestionState();
  };

  const handleNextQuestion = () => {
    if (isCorrect) {
      const newQuestions = [...questions];
      newQuestions.splice(currentQuestionIndex, 1);
      setQuestions(newQuestions);

      if (newQuestions.length === 0) {
        handleCompleteReview();
        return;
      }
      if (currentQuestionIndex >= newQuestions.length) {
        setCurrentQuestionIndex(0);
      }
    } else {
      const newQuestions = [...questions];
      const wrongQuestion = newQuestions.splice(currentQuestionIndex, 1)[0];
      const remainingQuestions = newQuestions.length - currentQuestionIndex;

      if (remainingQuestions > 0) {
        const randomOffset = Math.floor(Math.random() * remainingQuestions);
        const insertPosition = currentQuestionIndex + randomOffset;
        newQuestions.splice(insertPosition, 0, wrongQuestion);
      } else {
        newQuestions.push(wrongQuestion);
      }

      setQuestions(newQuestions);
      if (currentQuestionIndex + 1 >= newQuestions.length) {
        setCurrentQuestionIndex(0);
      } else {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }
    }

    resetQuestionState();
  };

  const resetQuestionState = () => {
    setUserAnswer("");
    setSelectedOptions([]);
    setShowResult(false);
    setIsCorrect(false);
    setFeedback("");
    setPronunciationBlob(null);
    setPronunciationAssessment(null);
  };

  const handleCompleteReview = async () => {
    if (!sessionId) return;
    try {
      await completeSession(sessionId);
      setIsCompleted(true);
    } catch (err) {
      console.error("Error completing review", err);
      setIsCompleted(true);
    }
  };

  const playAudio = (audioUrl) => {
    if (audioUrl) {
      new Audio(audioUrl).play();
    }
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Đang tải các từ cần ôn tập...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Ôn tập</h2>
          <p>{error}</p>
          <button onClick={() => navigate("/stats")}>Quay lại thống kê</button>
        </div>
      </div>
    );
  }

  if (isCompleted) {
    return (
      <div className={styles.container}>
        <CompletionScreen
          title="Hoàn thành ôn tập!"
          message="Bạn đã ôn xong tất cả các từ đến hạn hôm nay. Hẹn gặp bạn trong lần ôn tiếp theo."
          buttonText="Quay lại trang thống kê"
          onButtonClick={() => navigate("/stats")}
        />
      </div>
    );
  }

  if (!sessionData || !currentQuestion) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Không tìm thấy câu hỏi ôn tập</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <ProgressHeader
        onBackClick={() => navigate("/stats")}
        backButtonText="← Quay lại thống kê"
        progress={((sessionData.total_questions - questions.length) / sessionData.total_questions) * 100}
      />

      {/* Question Content */}
      <div className={styles.questionContainer}>
        <h2 className={styles.questionTitle}>{currentQuestion.title}</h2>

        {currentQuestion.type === "audio_multiple_choice" && (
          <AudioMultipleChoiceQuestion
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
            showResult={showResult}
            playAudio={playAudio}
            onClickSfx={playClick}
          />
        )}

        {currentQuestion.type === "definition_to_word" && (
          <DefinitionToWordQuestion
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
            showResult={showResult}
            onClickSfx={playClick}
          />
        )}

        {currentQuestion.type === "definition_to_input" && (
          <DefinitionToInputQuestion
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
            showResult={showResult}
            isCorrect={isCorrect}
            onClickSfx={playClick}
          />
        )}

        {currentQuestion.type === "word_definition_matching" && (
          <WordDefinitionMatchingQuestion
            question={currentQuestion}
            selectedOptions={selectedOptions}
            setSelectedOptions={setSelectedOptions}
            showResult={showResult}
            onClickSfx={playClick}
          />
        )}

        {currentQuestion.type === "pronunciation" && (
          <PronunciationQuestion
            question={currentQuestion}
            blob={pronunciationBlob}
            setBlob={setPronunciationBlob}
            assessment={pronunciationAssessment}
            showResult={showResult}
            disabled={isAssessingPronunciation || showResult}
          />
        )}

        {/* Result Display */}
        {showResult && (
          <ResultDisplay
            isCorrect={isCorrect}
            feedback={feedback}
            questionType={currentQuestion.type}
            pronunciationAssessment={pronunciationAssessment}
          />
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          {!showResult ? (
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button
                className={styles.submitBtn}
                onClick={handleAnswerSubmit}
                disabled={
                  (currentQuestion.type === "definition_to_input" && !userAnswer.trim()) ||
                  (currentQuestion.type === "word_definition_matching" && selectedOptions.length < 2) ||
                  (currentQuestion.type === "pronunciation" && !pronunciationBlob) ||
                  (currentQuestion.type === "pronunciation" && isAssessingPronunciation)
                }
              >
                Kiểm tra
              </button>
              {currentQuestion.type === "pronunciation" && (
                <button className={styles.nextBtn} onClick={handleSkipPronunciation}>
                  Bỏ qua
                </button>
              )}
            </div>
          ) : currentQuestion.type === "pronunciation" ? (
            <div style={{ display: "flex", gap: 8 }}>
              <button
                className={styles.submitBtn}
                onClick={() => {
                  setShowResult(false);
                  setIsCorrect(false);
                  setPronunciationAssessment(null);
                  setPronunciationBlob(null);
                }}
              >
                Ghi âm lại
              </button>
              <button className={styles.nextBtn} onClick={handleNextQuestion}>
                {questions.length <= 1 ? "Hoàn thành" : "Câu tiếp theo"}
              </button>
            </div>
          ) : (
            <button className={styles.nextBtn} onClick={handleNextQuestion}>
              {questions.length <= 1 ? "Hoàn thành" : "Câu tiếp theo"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ReviewPage;


