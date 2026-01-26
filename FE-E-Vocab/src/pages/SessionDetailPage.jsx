import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getSessionDetail } from "../services/learningService";
import { ArrowLeft, CheckCircle, XCircle, Clock } from "lucide-react";
import styles from "./SessionDetailPage.module.css";
import { useDocumentTitle } from '../hooks/useDocumentTitle';

const SessionDetailPage = () => {
  useDocumentTitle('Chi tiết phiên học');
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSessionDetail = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await getSessionDetail(sessionId);
        setSession(data);
      } catch (err) {
        setError("Không thể tải chi tiết phiên học. Vui lòng thử lại.");
        console.error("Error fetching session detail:", err);
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      fetchSessionDetail();
    }
  }, [sessionId]);

  const formatDate = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getModeName = (mode) => {
    switch (mode) {
      case "practice":
        return "Học từ vựng";
      case "review":
        return "Ôn tập";
      case "exam":
        return "Kiểm tra";
      default:
        return "Học từ vựng";
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Đang tải...</div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || "Không tìm thấy phiên học"}</div>
        <button className={styles.backBtn} onClick={() => navigate("/stats")}>
          Quay lại
        </button>
      </div>
    );
  }

  // Tạo map từ question id đến user answer
  const answerMap = {};
  session.user_answers?.forEach((answer) => {
    answerMap[answer.question] = answer;
  });

  // Sắp xếp questions theo order
  const sortedQuestions = [...(session.questions || [])].sort(
    (a, b) => a.order - b.order
  );

  const correctCount = session.user_answers?.filter(
    (answer) => answer.is_correct
  ).length || 0;

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate("/stats")}>
          <ArrowLeft size={20} />
          Quay lại
        </button>
        <h2>Chi tiết phiên học</h2>
      </div>

      {/* Thông tin phiên học */}
      <div className={styles.sessionInfo}>
        <div className={styles.infoCard}>
          <div className={styles.infoRow}>
            <span className={styles.label}>Loại phiên học:</span>
            <span className={styles.value}>{getModeName(session.mode)}</span>
          </div>
          {session.topic && (
            <div className={styles.infoRow}>
              <span className={styles.label}>Chủ đề:</span>
              <span className={styles.value}>{session.topic.title || `ID: ${session.topic}`}</span>
            </div>
          )}
          <div className={styles.infoRow}>
            <span className={styles.label}>Thời gian bắt đầu:</span>
            <span className={styles.value}>{formatDate(session.started_at)}</span>
          </div>
          {session.completed_at && (
            <div className={styles.infoRow}>
              <span className={styles.label}>Thời gian hoàn thành:</span>
              <span className={styles.value}>{formatDate(session.completed_at)}</span>
            </div>
          )}
          <div className={styles.infoRow}>
            <span className={styles.label}>Tổng số câu hỏi:</span>
            <span className={styles.value}>{session.total_questions}</span>
          </div>
          <div className={styles.infoRow}>
            <span className={styles.label}>Điểm số yêu cầu:</span>
            <span className={styles.value}>{session.pass_score}%</span>
          </div>
        </div>

        {/* Kết quả */}
        {session.completed_at && (
          <div className={styles.resultCard}>
            <div className={styles.resultHeader}>
              <h3>Kết quả</h3>
              <div
                className={`${styles.statusBadge} ${
                  session.is_passed ? styles.passed : styles.failed
                }`}
              >
                {session.is_passed ? (
                  <>
                    <CheckCircle size={16} />
                    Đạt
                  </>
                ) : (
                  <>
                    <XCircle size={16} />
                    Chưa đạt
                  </>
                )}
              </div>
            </div>
            <div className={styles.resultStats}>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Điểm số:</span>
                <span className={styles.statValue}>
                  {session.score ? Math.round(session.score) : 0}%
                </span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Số câu đúng:</span>
                <span className={styles.statValue}>
                  {correctCount}/{session.total_questions}
                </span>
              </div>
            </div>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{
                  width: `${session.score || 0}%`,
                  backgroundColor: session.is_passed ? "#10b981" : "#ef4444",
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Danh sách câu hỏi */}
      <div className={styles.questionsSection}>
        <h3>Câu hỏi và câu trả lời</h3>
        <div className={styles.questionsList}>
          {sortedQuestions.map((question, index) => {
            const userAnswer = answerMap[question.id];
            const isCorrect = userAnswer?.is_correct || false;

            return (
              <div
                key={question.id}
                className={`${styles.questionCard} ${
                  isCorrect ? styles.correct : styles.incorrect
                }`}
              >
                <div className={styles.questionHeader}>
                  <span className={styles.questionNumber}>
                    Câu {index + 1}
                  </span>
                  <span
                    className={`${styles.questionType} ${
                      isCorrect ? styles.typeCorrect : styles.typeIncorrect
                    }`}
                  >
                    {isCorrect ? (
                      <>
                        <CheckCircle size={16} />
                        Đúng
                      </>
                    ) : (
                      <>
                        <XCircle size={16} />
                        Sai
                      </>
                    )}
                  </span>
                </div>

                 <div className={styles.questionContent}>
                   {/* Hiển thị câu hỏi dựa trên question_type */}
                   {(() => {
                     const content = question.content || {};
                     const prompt = content.prompt || {};
                     const questionType = question.question_type || '';

                     // Helper function để normalize correct answer
                     const getCorrectAnswerValue = (correctAnswer) => {
                       if (correctAnswer == null) return null;
                       if (typeof correctAnswer === 'object' && correctAnswer !== null) {
                         return correctAnswer.answer ?? null;
                       }
                       return correctAnswer;
                     };

                     // Helper function để normalize user selected option
                     const normalizeUserOption = (selectedOption) => {
                       if (selectedOption == null) return null;
                       // Thử parse thành số trước
                       if (typeof selectedOption === 'number') return selectedOption;
                       const num = parseInt(selectedOption, 10);
                       // Nếu parse được thành số hợp lệ, trả về số, không thì trả về string
                       return isNaN(num) ? selectedOption : num;
                     };

                     // Helper function để kiểm tra option có phải đáp án đúng không
                     const checkIsCorrectOption = (correctAnswerValue, optIndex, option) => {
                       if (correctAnswerValue == null) return false;
                       // So sánh cả số và string
                       return correctAnswerValue === optIndex || 
                              correctAnswerValue === String(optIndex) ||
                              correctAnswerValue === option;
                     };

                     // Helper function để kiểm tra option có phải đáp án user chọn không
                     const checkIsUserAnswer = (normalizedUserOption, optIndex, option, answerText) => {
                       if (normalizedUserOption == null && !answerText) return false;
                       // So sánh với index (cả số và string)
                       return normalizedUserOption === optIndex ||
                              normalizedUserOption === String(optIndex) ||
                              normalizedUserOption === option ||
                              answerText === option;
                     };

                     // Listening: hiển thị word và options
                     if (questionType === 'listening') {
                       const correctAnswerValue = getCorrectAnswerValue(question.correct_answer);
                       const normalizedUserOption = normalizeUserOption(userAnswer?.selected_option);
                       
                       return (
                         <>
                           {prompt.word && (
                             <div className={styles.questionBody}>
                               <p><strong>Từ:</strong> {prompt.word}</p>
                               {prompt.pronunciation && (
                                 <p className={styles.phonetic}>/{prompt.pronunciation}/</p>
                               )}
                               {prompt.audio_url && (
                                 <p className={styles.audioNote}>Có file audio</p>
                               )}
                             </div>
                           )}
                           {prompt.options && prompt.options.length > 0 && (
                             <div className={styles.optionsList}>
                               <p className={styles.optionsLabel}>Chọn nghĩa đúng:</p>
                               {prompt.options.map((option, optIndex) => {
                                 const isCorrectOption = checkIsCorrectOption(correctAnswerValue, optIndex, option);
                                 const isUserAnswer = checkIsUserAnswer(normalizedUserOption, optIndex, option, userAnswer?.answer_text);
                                 const isUserWrong = isUserAnswer && !isCorrectOption;

                                 return (
                                   <div
                                     key={optIndex}
                                     className={`${styles.option} ${
                                       isCorrectOption ? styles.correctOption : ""
                                     } ${isUserWrong ? styles.wrongAnswer : ""}`}
                                   >
                                     <span className={styles.optionLabel}>
                                       {String.fromCharCode(65 + optIndex)}.
                                     </span>
                                     <span>{option}</span>
                                     {isCorrectOption && (
                                       <CheckCircle
                                         size={16}
                                         className={styles.optionIcon}
                                       />
                                     )}
                                     {isUserWrong && (
                                       <XCircle size={16} className={styles.optionIcon} />
                                     )}
                                   </div>
                                 );
                               })}
                             </div>
                           )}
                         </>
                       );
                     }

                     // Reading: hiển thị definition và options
                     if (questionType === 'reading') {
                       const correctAnswerValue = getCorrectAnswerValue(question.correct_answer);
                       const normalizedUserOption = normalizeUserOption(userAnswer?.selected_option);
                       
                       return (
                         <>
                           {prompt.definition && (
                             <div className={styles.questionBody}>
                               <p><strong>Nghĩa:</strong> {prompt.definition}</p>
                               <p className={styles.questionPrompt}>Chọn từ phù hợp:</p>
                             </div>
                           )}
                           {prompt.options && prompt.options.length > 0 && (
                             <div className={styles.optionsList}>
                               {prompt.options.map((option, optIndex) => {
                                 const isCorrectOption = checkIsCorrectOption(correctAnswerValue, optIndex, option);
                                 const isUserAnswer = checkIsUserAnswer(normalizedUserOption, optIndex, option, userAnswer?.answer_text);
                                 const isUserWrong = isUserAnswer && !isCorrectOption;

                                 return (
                                   <div
                                     key={optIndex}
                                     className={`${styles.option} ${
                                       isCorrectOption ? styles.correctOption : ""
                                     } ${isUserWrong ? styles.wrongAnswer : ""}`}
                                   >
                                     <span className={styles.optionLabel}>
                                       {String.fromCharCode(65 + optIndex)}.
                                     </span>
                                     <span>{option}</span>
                                     {isCorrectOption && (
                                       <CheckCircle
                                         size={16}
                                         className={styles.optionIcon}
                                       />
                                     )}
                                     {isUserWrong && (
                                       <XCircle size={16} className={styles.optionIcon} />
                                     )}
                                   </div>
                                 );
                               })}
                             </div>
                           )}
                         </>
                       );
                     }

                    // Writing: hiển thị definition
                    if (questionType === 'writing') {
                      return (
                        <>
                          {prompt.definition && (
                            <div className={styles.questionBody}>
                              <p><strong>Nghĩa:</strong> {prompt.definition}</p>
                              {prompt.hint && (
                                <p className={styles.hint}><em>Gợi ý: {prompt.hint}</em></p>
                              )}
                              <p className={styles.questionPrompt}>Nhập từ tương ứng:</p>
                            </div>
                          )}
                        </>
                      );
                    }

                    // Matching: hiển thị words và definitions với các cặp nối
                    if (questionType === 'matching') {
                      // Parse user answer
                      let userAnswerObj = null;
                      if (userAnswer?.answer_text) {
                        try {
                          if (typeof userAnswer.answer_text === 'string') {
                            userAnswerObj = JSON.parse(userAnswer.answer_text);
                          } else {
                            userAnswerObj = userAnswer.answer_text;
                          }
                        } catch (e) {
                          userAnswerObj = null;
                        }
                      }

                      // Parse correct answer
                      let correctAnswerObj = null;
                      try {
                        const correctAnswer = question.correct_answer;
                        if (typeof correctAnswer === 'object' && correctAnswer !== null) {
                          correctAnswerObj = correctAnswer.answer || correctAnswer;
                        } else if (typeof correctAnswer === 'string') {
                          correctAnswerObj = JSON.parse(correctAnswer);
                        } else {
                          correctAnswerObj = correctAnswer;
                        }
                      } catch (e) {
                        correctAnswerObj = null;
                      }

                      // Tạo danh sách các cặp từ-nghĩa với trạng thái đúng/sai
                      const matchingPairs = [];
                      if (prompt.words && userAnswerObj && correctAnswerObj) {
                        prompt.words.forEach((word) => {
                          const userDefinition = userAnswerObj[word];
                          const correctDefinition = correctAnswerObj[word];
                          const isCorrect = userDefinition === correctDefinition;
                          
                          if (userDefinition) {
                            matchingPairs.push({
                              word,
                              definition: userDefinition,
                              isCorrect,
                            });
                          }
                        });
                      }

                      return (
                        <>
                          {prompt.words && prompt.definitions && (
                            <div className={styles.questionBody}>
                              <p className={styles.questionPrompt}>Nối từ với nghĩa phù hợp:</p>
                              {matchingPairs.length > 0 ? (
                                <div className={styles.matchingPairsList}>
                                  {matchingPairs.map((pair, idx) => (
                                    <div
                                      key={idx}
                                      className={`${styles.matchingPair} ${
                                        pair.isCorrect ? styles.matchingPairCorrect : styles.matchingPairIncorrect
                                      }`}
                                    >
                                      <span className={styles.matchingPairWord}>{pair.word}</span>
                                      <span className={styles.matchingPairArrow}>→</span>
                                      <span className={styles.matchingPairDefinition}>{pair.definition}</span>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <div className={styles.matchingContainer}>
                                  <div className={styles.matchingColumn}>
                                    <h4>Từ:</h4>
                                    {prompt.words.map((word, idx) => (
                                      <div key={idx} className={styles.matchingItem}>
                                        {word}
                                      </div>
                                    ))}
                                  </div>
                                  <div className={styles.matchingColumn}>
                                    <h4>Nghĩa:</h4>
                                    {prompt.definitions.map((def, idx) => (
                                      <div key={idx} className={styles.matchingItem}>
                                        {def}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      );
                    }

                    // Fallback: hiển thị dữ liệu raw nếu không match
                    return (
                      <div className={styles.questionBody}>
                        {typeof content === 'string' ? (
                          <div dangerouslySetInnerHTML={{ __html: content }} />
                        ) : content.title ? (
                          <p><strong>{content.title}</strong></p>
                        ) : (
                          <p><em>Loại câu hỏi: {questionType}</em></p>
                        )}
                        {content.options && (
                          <div className={styles.optionsList}>
                            {content.options.map((option, optIndex) => (
                              <div key={optIndex} className={styles.option}>
                                <span className={styles.optionLabel}>
                                  {String.fromCharCode(65 + optIndex)}.
                                </span>
                                <span>{option}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  {/* Hiển thị đáp án của người dùng (bỏ qua matching vì đã hiển thị trong câu hỏi) */}
                  {userAnswer?.answer_text && (question.question_type || '') !== 'matching' && (
                    <div className={styles.userAnswer}>
                      <span className={styles.userAnswerLabel}>
                        Câu trả lời của bạn:
                      </span>
                      <span>{userAnswer.answer_text}</span>
                    </div>
                  )}

                  {question.explanation && (
                    <div className={styles.explanation}>
                      <span className={styles.explanationLabel}>
                        Giải thích:
                      </span>
                      <span>{question.explanation}</span>
                    </div>
                  )}

                  {userAnswer?.time_spent && (
                    <div className={styles.timeSpent}>
                      <Clock size={14} />
                      <span>Thời gian: {Math.round(userAnswer.time_spent)}s</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SessionDetailPage;

