import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import styles from "./ExamPage.module.css";
import { FaCheck, FaTimes, FaArrowRight } from "react-icons/fa";
import { 
  createExamSession, 
  getSessionQuestions, 
  submitAnswer, 
  completeSession,
  assessPronunciation 
} from "../services/learningService";
import { mapQuestions, getBackendType, mapAnswerToBackend } from "../services/questionMapper";
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import {
  AudioMultipleChoiceQuestion,
  DefinitionToWordQuestion,
  DefinitionToInputQuestion,
  WordDefinitionMatchingQuestion,
  PronunciationQuestion
} from '../components/Questions';
import { ProgressHeader } from '../components/Common';

function ExamPage() {
  useDocumentTitle('Kiểm tra');
  const [sessionId, setSessionId] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [userAnswer, setUserAnswer] = useState("");
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [userAnswers, setUserAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [finalResult, setFinalResult] = useState(null);
  const [pronunciationBlob, setPronunciationBlob] = useState(null);
  const [isAssessingPronunciation, setIsAssessingPronunciation] = useState(false);

  const { topicId } = useParams();
  const navigate = useNavigate();

  // Reset dữ liệu phát âm khi chuyển câu hỏi
  useEffect(() => {
    setPronunciationBlob(null);
    setQuestionStartTime(Date.now());
  }, [currentQuestionIndex]);

  // Fetch exam questions
  const fetchExamQuestions = useCallback(async () => {
    const token = localStorage.getItem("accessToken") || sessionStorage.getItem("accessToken");
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      setIsLoading(true);
      
      // 1. Tạo exam session với các tùy chọn mặc định
      const sessionResponse = await createExamSession(parseInt(topicId), {
        time_limit: 10,  // 10 phút
        total_questions: 20,
        pass_score: 80
      });
      
      setSessionId(sessionResponse.session_id);
      setSessionData(sessionResponse);
      setTimeRemaining(sessionResponse.time_limit * 60); // Chuyển sang giây

      // 2. Lấy danh sách câu hỏi
      const questionsResponse = await getSessionQuestions(sessionResponse.session_id);
      
      // 3. Map câu hỏi sang frontend format
      const mappedQuestions = mapQuestions(questionsResponse.questions);
      setQuestions(mappedQuestions);
      
      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching exam questions", err);
      setError(err.response?.data?.error || "Có lỗi xảy ra khi tải bài kiểm tra");
      setIsLoading(false);
    }
  }, [topicId, navigate]);

  useEffect(() => {
    fetchExamQuestions();
  }, [fetchExamQuestions]);

  // Timer countdown
  useEffect(() => {
    if (timeRemaining <= 0 || isCompleted) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleSubmitExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining, isCompleted]);

  // Track question start time
  useEffect(() => {
    if (questions.length > 0) {
      setQuestionStartTime(Date.now());
    }
  }, [currentQuestionIndex, questions]);

  const currentQuestion = questions[currentQuestionIndex];

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSubmit = async () => {
    if (!currentQuestion || isSubmitting) return;

    const timeSpent = (Date.now() - questionStartTime) / 1000;
    const backendType = getBackendType(currentQuestion.type);
    
    let answer = userAnswer;
    let pronunciationScore = null;

    // Xử lý từng loại câu hỏi
    switch (currentQuestion.type) {
      case 'audio_multiple_choice':
      case 'definition_to_word':
        answer = userAnswer;
        break;

      case 'definition_to_input':
        answer = userAnswer.trim();
        break;

      case 'word_definition_matching':
        answer = mapAnswerToBackend(backendType, selectedOptions);
        break;

      case 'pronunciation':
        if (!pronunciationBlob) return;
        
        try {
          setIsAssessingPronunciation(true);
          const assessment = await assessPronunciation(pronunciationBlob, currentQuestion.word || currentQuestion.target_word);
          pronunciationScore = assessment.score;
          answer = pronunciationScore; // Gửi pronunciation_score làm answer
        } catch (e) {
          console.error('Pronunciation assess error:', e);
          setIsAssessingPronunciation(false);
          return;
        } finally {
          setIsAssessingPronunciation(false);
        }
        break;

      default:
        break;
    }

    // Tạo đáp án hiện tại
    const currentAnswerData = {
      answer,
      time_spent: timeSpent,
      pronunciation_score: pronunciationScore
    };

    // Lưu đáp án vào userAnswers
    const updatedAnswers = {
      ...userAnswers,
      [currentQuestion.id]: currentAnswerData
    };
    setUserAnswers(updatedAnswers);

    // Kiểm tra xem có phải câu hỏi cuối không
    const isLastQuestion = currentQuestionIndex >= questions.length - 1;
    
    if (isLastQuestion) {
      // Nếu là câu cuối, submit ngay với đáp án đã cập nhật
      await handleSubmitExam(updatedAnswers);
    } else {
      // Chuyển sang câu tiếp theo
      handleNextQuestion();
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setUserAnswer("");
      setSelectedOptions([]);
      setPronunciationBlob(null);
    }
  };

  const handleSubmitExam = async (answersToSubmit = null) => {
    if (isSubmitting || !sessionId) return;

    setIsSubmitting(true);

    try {
      // Sử dụng answersToSubmit nếu được truyền vào, nếu không thì dùng userAnswers state
      const answers = answersToSubmit || userAnswers;
      
      // Gửi tất cả câu trả lời lên server
      for (const [questionId, answerData] of Object.entries(answers)) {
        await submitAnswer(
          sessionId,
          parseInt(questionId),
          answerData.answer,
          answerData.time_spent,
          answerData.pronunciation_score
        );
      }

      // Hoàn thành session và nhận kết quả
      const result = await completeSession(sessionId);
      setFinalResult(result);
      setIsCompleted(true);
    } catch (err) {
      console.error("Error submitting exam", err);
      setError(err.response?.data?.error || "Có lỗi xảy ra khi nộp bài");
      setIsSubmitting(false);
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
        <div className={styles.loading}>Đang tải bài kiểm tra...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Lỗi</h2>
          <p>{error}</p>
          <button onClick={() => navigate(`/topic/${topicId}`)}>
            Quay lại
          </button>
        </div>
      </div>
    );
  }

  // Hiển thị màn hình kết quả
  if (isCompleted && finalResult) {
    return (
      <div className={styles.container}>
        <div className={styles.resultScreen}>
          <div className={styles.resultContent}>
            <div className={styles.resultIcon}>
              {finalResult.is_passed ? <FaCheck size={64} color="#22c55e" /> : <FaTimes size={64} color="#ef4444" />}
            </div>
            <h1 className={styles.resultTitle}>
              {finalResult.is_passed ? "Chúc mừng! Bạn đã đạt!" : "Rất tiếc! Bạn chưa đạt"}
            </h1>
            <div className={styles.resultStats}>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>Điểm số</div>
                <div className={styles.statValue}>{finalResult.score?.toFixed(1) || 0}/100</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>Điểm đạt</div>
                <div className={styles.statValue}>{sessionData?.pass_score || 80}</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>Câu đúng</div>
                <div className={styles.statValue}>{finalResult.correct_count || 0}/{finalResult.total_questions || questions.length}</div>
              </div>
            </div>
            <div className={styles.resultActions}>
              <button 
                className={styles.primaryButton}
                onClick={() => navigate(`/topic/${topicId}`)}
              >
                Quay lại danh sách từ vựng
              </button>
              <button 
                className={styles.secondaryButton}
                onClick={() => window.location.reload()}
              >
                Làm lại
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!sessionData || !currentQuestion) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Không tìm thấy câu hỏi</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <ProgressHeader
        onBackClick={() => {
          if (window.confirm("Bạn có chắc muốn thoát? Bài kiểm tra sẽ không được lưu.")) {
            navigate(`/topic/${topicId}`);
          }
        }}
        backButtonText="← Quay lại"
        progress={((currentQuestionIndex + 1) / questions.length) * 100}
        showTimer={true}
        timerText={formatTime(timeRemaining)}
        questionCounter={`Câu ${currentQuestionIndex + 1}/${questions.length}`}
      />

      {/* Question Content */}
      <div className={styles.questionContainer}>
        <h2 className={styles.questionTitle}>{currentQuestion.title}</h2>

        {/* Render question based on type */}
        {currentQuestion.type === 'audio_multiple_choice' && (
          <AudioMultipleChoiceQuestion
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
            playAudio={playAudio}
          />
        )}

        {currentQuestion.type === 'definition_to_word' && (
          <DefinitionToWordQuestion
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
          />
        )}

        {currentQuestion.type === 'definition_to_input' && (
          <DefinitionToInputQuestion
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
          />
        )}

        {currentQuestion.type === 'word_definition_matching' && (
          <WordDefinitionMatchingQuestion
            question={currentQuestion}
            selectedOptions={selectedOptions}
            setSelectedOptions={setSelectedOptions}
          />
        )}

        {currentQuestion.type === 'pronunciation' && (
          <PronunciationQuestion
            question={currentQuestion}
            blob={pronunciationBlob}
            setBlob={setPronunciationBlob}
            disabled={isAssessingPronunciation}
          />
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          <button
            className={styles.submitBtn}
            onClick={handleAnswerSubmit}
            disabled={
              isSubmitting ||
              isAssessingPronunciation ||
              (currentQuestion.type === 'definition_to_input' && !userAnswer.trim()) ||
              (currentQuestion.type === 'word_definition_matching' && selectedOptions.length < 2) ||
              (currentQuestion.type === 'pronunciation' && !pronunciationBlob) ||
              (currentQuestion.type === 'audio_multiple_choice' && userAnswer === "") ||
              (currentQuestion.type === 'definition_to_word' && userAnswer === "")
            }
          >
            {currentQuestionIndex + 1 >= questions.length ? "Nộp bài" : "Câu tiếp theo"}
            <FaArrowRight />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ExamPage;
