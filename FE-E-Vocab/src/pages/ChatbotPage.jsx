import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./ChatbotPage.module.css";
import env from "../config/env";
import { useDocumentTitle } from '../hooks/useDocumentTitle';

const PENDING_QUIZ_KEY = "evocab_chatbot_pending_quiz";
const PENDING_QUIZ_INTRO_KEY = "evocab_chatbot_pending_quiz_intro";
const ACTIVE_QUIZ_KEY = "evocab_chatbot_active_quiz";
const QUIZ_PROGRESS_KEY = "evocab_chatbot_quiz_progress";

const OPTION_LABELS = ["A", "B", "C", "D", "E", "F"];

export default function ChatbotPage() {
  useDocumentTitle('Chatbot');
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [pendingQuiz, setPendingQuiz] = useState(null);
  const [pendingQuizIntro, setPendingQuizIntro] = useState("");
  const [activeQuiz, setActiveQuiz] = useState([]);
  const [quizProgress, setQuizProgress] = useState(0);
  const [isAnswering, setIsAnswering] = useState(false);
  const [quizResults, setQuizResults] = useState([]);
  const [showClearWarning, setShowClearWarning] = useState(false);
  const endRef = useRef(null);
  const isQuizActive = activeQuiz.length > 0 && quizProgress < activeQuiz.length;
  const currentQuestion = isQuizActive ? activeQuiz[quizProgress] : null;

  // Kiểm tra đăng nhập và load lịch sử
  useEffect(() => {
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    
    if (!token) {
      // Chưa đăng nhập, chuyển đến trang login
      navigate('/login');
      return;
    }

    // Load lịch sử từ API
    const loadHistory = async () => {
      try {
        const response = await fetch(`${env.API_BASE_URL}/history/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          if (data.messages && Array.isArray(data.messages)) {
            setMessages(data.messages);
          }
        } else if (response.status === 401) {
          // Token hết hạn, chuyển đến login
          navigate('/login');
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadHistory();

    // Load quiz state từ localStorage (tạm thời giữ lại)
    try {
      const storedQuiz = localStorage.getItem(PENDING_QUIZ_KEY);
      if (storedQuiz) {
        try {
          const parsedQuiz = JSON.parse(storedQuiz);
          if (
            Array.isArray(parsedQuiz) &&
            parsedQuiz.length > 0 &&
            parsedQuiz.every((item) => item && typeof item === "object" && Array.isArray(item.options))
          ) {
            setPendingQuiz(parsedQuiz);
          }
        } catch (error) {
          console.warn("Unable to parse pending quiz", error);
        }
      }

      const storedIntro = localStorage.getItem(PENDING_QUIZ_INTRO_KEY);
      if (storedIntro) {
        setPendingQuizIntro(storedIntro);
      }

      const storedActiveQuiz = localStorage.getItem(ACTIVE_QUIZ_KEY);
      if (storedActiveQuiz) {
        try {
          const parsedActiveQuiz = JSON.parse(storedActiveQuiz);
          if (
            Array.isArray(parsedActiveQuiz) &&
            parsedActiveQuiz.length > 0 &&
            parsedActiveQuiz.every((item) => item && typeof item === "object" && Array.isArray(item.options))
          ) {
            setActiveQuiz(parsedActiveQuiz);
          }
        } catch (error) {
          console.warn("Unable to parse active quiz", error);
        }
      }

      const storedProgress = localStorage.getItem(QUIZ_PROGRESS_KEY);
      if (storedProgress) {
        const parsedProgress = Number(storedProgress);
        if (!Number.isNaN(parsedProgress) && parsedProgress >= 0) {
          setQuizProgress(parsedProgress);
        }
      }
    } catch (error) {
      console.warn("Unable to load quiz state", error);
    }
  }, [navigate]);

  // Không cần lưu messages vào localStorage nữa, đã lưu vào Redis

  useEffect(() => {
    if (pendingQuiz && pendingQuiz.length) {
      localStorage.setItem(PENDING_QUIZ_KEY, JSON.stringify(pendingQuiz));
    } else {
      localStorage.removeItem(PENDING_QUIZ_KEY);
    }
  }, [pendingQuiz]);

  useEffect(() => {
    if (pendingQuizIntro) {
      localStorage.setItem(PENDING_QUIZ_INTRO_KEY, pendingQuizIntro);
    } else {
      localStorage.removeItem(PENDING_QUIZ_INTRO_KEY);
    }
  }, [pendingQuizIntro]);

  useEffect(() => {
    if (activeQuiz && activeQuiz.length) {
      localStorage.setItem(ACTIVE_QUIZ_KEY, JSON.stringify(activeQuiz));
    } else {
      localStorage.removeItem(ACTIVE_QUIZ_KEY);
    }
  }, [activeQuiz]);

  useEffect(() => {
    if (activeQuiz && activeQuiz.length) {
      localStorage.setItem(QUIZ_PROGRESS_KEY, String(quizProgress));
    } else {
      localStorage.removeItem(QUIZ_PROGRESS_KEY);
    }
  }, [quizProgress, activeQuiz]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (activeQuiz && activeQuiz.length && quizProgress >= activeQuiz.length) {
      setActiveQuiz([]);
      setQuizProgress(0);
    }
  }, [activeQuiz, quizProgress]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;

    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    if (!token) {
      navigate('/login');
      return;
    }

    // Thêm user message vào UI ngay (optimistic update)
    const timestamp = Date.now();
    const userMsg = { role: "user", content: text, timestamp };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch(`${env.API_BASE_URL}/chat/`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ message: text }),
        credentials: "include",
      });

      if (resp.status === 401) {
        // Token hết hạn
        navigate('/login');
        return;
      }

      const data = await resp.json();
      const replyPayload = data?.reply;

      // Thêm bot reply vào messages (backend đã tự động lưu vào Redis)
      if (replyPayload && typeof replyPayload === "object" && !Array.isArray(replyPayload)) {
        if (replyPayload.type === "quiz_offer") {
          const introText = replyPayload.message ?? "Bạn đã sẵn sàng cho thử thách từ vựng mới chưa?";
          const introMessage = {
            role: "assistant",
            content: introText,
            timestamp: Date.now(),
            type: "quiz_offer",
          };
          setMessages((prev) => [...prev, introMessage]);
          setPendingQuiz(replyPayload.questions ?? []);
          setPendingQuizIntro(introText);
          return;
        }

        if (replyPayload.type === "pronunciation") {
          const pronunciationMessage = {
            role: "assistant",
            content: replyPayload.message,
            timestamp: Date.now(),
            type: "pronunciation",
            audio_url: replyPayload.audio_url,
            word: replyPayload.word,
            phonetic: replyPayload.phonetic,
          };
          setMessages((prev) => [...prev, pronunciationMessage]);
          return;
        }

        if (typeof replyPayload.message === "string") {
          const botText = replyPayload.message;
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: botText, timestamp: Date.now() },
          ]);
          return;
        }
      }

      // Nếu là string thông thường
      const botText =
        typeof replyPayload === "string"
          ? replyPayload
          : "Xin lỗi, đã có lỗi xảy ra.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: botText, timestamp: Date.now() },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Không thể kết nối tới chatbot.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setShowClearWarning(true);
  };

  const confirmClear = async () => {
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      // Xóa lịch sử từ API
      const response = await fetch(`${env.API_BASE_URL}/history/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (response.ok) {
        setMessages([]);
        localStorage.removeItem(PENDING_QUIZ_KEY);
        localStorage.removeItem(PENDING_QUIZ_INTRO_KEY);
        localStorage.removeItem(ACTIVE_QUIZ_KEY);
        localStorage.removeItem(QUIZ_PROGRESS_KEY);
        setPendingQuiz(null);
        setPendingQuizIntro("");
        setActiveQuiz([]);
        setQuizProgress(0);
        setQuizResults([]);
      }
    } catch (error) {
      console.error('Error clearing chat history:', error);
    } finally {
      setShowClearWarning(false);
    }
  };

  const cancelClear = () => {
    setShowClearWarning(false);
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startQuiz = () => {
    if (!pendingQuiz || !pendingQuiz.length) return;

    const totalQuestions = pendingQuiz.length;
    const now = Date.now();
    const kickoffMessage = {
      role: "assistant",
      content:
        `Tuyệt! Cùng chinh phục ${totalQuestions} câu hỏi nào. Chọn đáp án phù hợp cho từng câu ngay bên dưới nhé!`,
      timestamp: now,
      type: "quiz_start",
    };
    setMessages((prev) => [...prev, kickoffMessage]);
    setActiveQuiz(pendingQuiz);
    setQuizProgress(0);
    setQuizResults([]);
    setPendingQuiz(null);
    setPendingQuizIntro("");
  };

  const cancelQuiz = () => {
    setPendingQuiz(null);
    setPendingQuizIntro("");
    setQuizResults([]);
    const timestamp = Date.now();
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: "Khi nào bạn sẵn sàng, hãy nhắn tôi để bắt đầu quiz nhé!",
        timestamp,
        type: "quiz_cancel",
      },
    ]);
  };

  const handleSelectAnswer = (optionIndex) => {
    if (!currentQuestion || isAnswering) return;

    setIsAnswering(true);

    const timestamp = Date.now();
    const selectedText = currentQuestion.options[optionIndex];
    const correctIndex = currentQuestion.answerIndex;
    const correctText = currentQuestion.options[correctIndex];
    const isCorrect = optionIndex === correctIndex;
    const explanation = currentQuestion.explanation || "";
    const questionLabel = `Câu ${quizProgress + 1}/${activeQuiz.length}: ${currentQuestion.prompt}`;

    const updatedResults = [
      ...quizResults,
      {
        prompt: currentQuestion.prompt,
        selected: selectedText,
        correct: correctText,
        isCorrect,
        explanation,
      },
    ];
    setQuizResults(updatedResults);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: questionLabel,
        timestamp,
        type: "quiz_question",
      },
      {
        role: "user",
        content: `Tôi chọn: ${selectedText}`,
        timestamp: timestamp + 1,
      },
      {
        role: "assistant",
        content: isCorrect
          ? `🎉 Chính xác! Đáp án đúng là "${correctText}".${explanation ? `\n${explanation}` : ""}`
          : `🤔 Chưa chính xác rồi. Đáp án đúng là "${correctText}".${explanation ? `\n${explanation}` : ""}`,
        timestamp: timestamp + 2,
        type: "quiz_feedback",
      },
    ]);

    const nextProgress = quizProgress + 1;
    if (nextProgress >= activeQuiz.length) {
      setActiveQuiz([]);
      setQuizProgress(0);

      const correctAnswers = updatedResults.filter((item) => item.isCorrect).length;
      const incorrectItems = updatedResults.filter((item) => !item.isCorrect);

      const breakdown = incorrectItems
        .map((item, index) =>
          `${index + 1}. ${item.prompt}\n   Bạn chọn: ${item.selected}\n   Đáp án đúng: ${item.correct}${item.explanation ? `\n   ${item.explanation}` : ""}`
        )
        .join("\n\n");

      const summaryMessage =
        incorrectItems.length === 0
          ? `Xuất sắc! Bạn trả lời đúng toàn bộ ${updatedResults.length} câu hỏi.`
          : `Bạn trả lời đúng ${correctAnswers}/${updatedResults.length} câu.\n\nCác câu cần xem lại:\n${breakdown}`;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: summaryMessage,
          timestamp: timestamp + 3,
          type: "quiz_summary",
        },
      ]);

      setQuizResults([]);
    } else {
      setQuizProgress(nextProgress);
    }

    setIsAnswering(false);
  };

  const composerClassName = `${styles.composer} ${isQuizActive ? styles.composerHidden : ""}`;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerTop}>
          <h1 className={styles.headerTitle}>E-Vocab Chat Coach</h1>
          <button
            type="button"
            className={`${styles.button} ${styles.secondary} ${styles.clearButton}`}
            onClick={handleClear}
            disabled={!messages.length && !pendingQuiz && !activeQuiz.length}
          >
            Dọn cuộc trò chuyện
          </button>
        </div>
        <p className={styles.headerDescription}>
          Trợ lý E-Vocab Chat Coach sẵn sàng hỗ trợ bạn giải nghĩa từ mới, gợi ý ví dụ
          và gửi những câu đố từ vựng thú vị để bạn luyện tập mỗi ngày.
        </p>
      </header>

      {loadingHistory && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '400px',
          fontSize: '16px',
          color: '#666'
        }}>
          Đang tải lịch sử chat...
        </div>
      )}

      {showClearWarning && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '8px',
            maxWidth: '400px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#333' }}>
              ⚠️ Xác nhận xóa lịch sử
            </h3>
            <p style={{ marginBottom: '24px', color: '#666', lineHeight: '1.5' }}>
              Bạn có chắc chắn muốn xóa toàn bộ lịch sử chat? Hành động này không thể hoàn tác.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={cancelClear}
                style={{
                  padding: '8px 16px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Hủy
              </button>
              <button
                onClick={confirmClear}
                style={{
                  padding: '8px 16px',
                  border: 'none',
                  borderRadius: '4px',
                  backgroundColor: '#dc3545',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Xóa
              </button>
            </div>
          </div>
        </div>
      )}

      <section className={styles.chatCard}>
        <div className={styles.messageList}>
          {!loadingHistory && messages.length === 0 && (
            <div className={styles.emptyState}>
              Hãy gửi tin nhắn đầu tiên để khám phá kho từ vựng cùng trợ lý của bạn!
            </div>
          )}
          {messages.map((m) => {
            const isUser = m.role === "user";
            const isPronunciation = m.type === "pronunciation" && m.audio_url;
            
            const handlePlayAudio = () => {
              if (m.audio_url) {
                const audio = new Audio(m.audio_url);
                audio.volume = 1.0; // Tăng volume lên tối đa (0.0 - 1.0)
                audio.play().catch((err) => {
                  console.warn("Không thể phát audio:", err);
                });
              }
            };

            return (
              <div
                key={m.timestamp}
                className={`${styles.messageRow} ${isUser ? styles.messageRowUser : ""}`}
              >
                <div
                  className={`${styles.messageBubble} ${
                    isUser ? styles.messageBubbleUser : styles.messageBubbleAssistant
                  }`}
                >
                  <div
                    dangerouslySetInnerHTML={{
                      __html: m.content.replace(/\n/g, "<br />"),
                    }}
                  />
                  {isPronunciation && (
                    <div style={{ marginTop: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                      <button
                        type="button"
                        onClick={handlePlayAudio}
                        style={{
                          background: "#4CAF50",
                          border: "none",
                          borderRadius: "50%",
                          width: "40px",
                          height: "40px",
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: "white",
                          fontSize: "18px",
                          transition: "background 0.2s",
                        }}
                        onMouseOver={(e) => (e.target.style.background = "#45a049")}
                        onMouseOut={(e) => (e.target.style.background = "#4CAF50")}
                        title="Nghe phát âm"
                      >
                        🔊
                      </button>
                      <span style={{ fontSize: "14px", color: "#666" }}>
                        Nhấn để nghe
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {loading && (
            <div className={`${styles.messageRow} ${styles.typingRow}`}>
              <div className={`${styles.messageBubble} ${styles.typingBubble}`}>
                <span className={styles.typingText}>Chatbot đang soạn trả lời</span>
                <span className={styles.typingDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </div>
            </div>
          )}
          <span ref={endRef} />
        </div>

        {pendingQuiz && pendingQuiz.length > 0 && (
          <div className={styles.quizPrompt}>
            <div>
              <strong>{pendingQuizIntro || "Bạn đã sẵn sàng cho thử thách quiz chưa?"}</strong>
            </div>
            <p>
              Bộ đề gồm {pendingQuiz.length} câu hỏi ngẫu nhiên giống như phần kiểm tra Ôn luyện. Nhấn
              "Bắt đầu thử thách" để hiển thị từng câu hỏi, hoặc "Để sau" nếu bạn muốn chuẩn bị thêm.
            </p>
            <div className={styles.quizActions}>
              <button
                type="button"
                className={`${styles.button} ${styles.primary}`}
                onClick={startQuiz}
              >
                Bắt đầu thử thách
              </button>
              <button
                type="button"
                className={`${styles.button} ${styles.secondary}`}
                onClick={cancelQuiz}
              >
                Để sau
              </button>
            </div>
          </div>
        )}

        {isQuizActive && currentQuestion && (
          <div className={styles.quizQuestion}>
            <div className={styles.quizQuestionHeader}>
              Câu {quizProgress + 1}/{activeQuiz.length}
            </div>
            <div className={styles.quizPromptText}>{currentQuestion.prompt}</div>
            {currentQuestion.meaning && (
              <div className={styles.quizMeaning}>
                Nghĩa: <span>{currentQuestion.meaning}</span>
              </div>
            )}
            {currentQuestion.pronunciation && (
              <div className={styles.quizMeta}>Phiên âm: {currentQuestion.pronunciation}</div>
            )}
            <div className={styles.quizOptions}>
              {currentQuestion.options.map((option, index) => (
                <button
                  key={`${currentQuestion.id}-${index}`}
                  type="button"
                  className={`${styles.button} ${styles.optionButton}`}
                  onClick={() => handleSelectAnswer(index)}
                  disabled={isAnswering}
                >
                  <span className={styles.optionLabel}>
                    {OPTION_LABELS[index] ?? index + 1}.
                  </span>
                  <span>{option}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className={composerClassName}>
          <div className={styles.textareaWrapper}>
            <textarea
              className={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={3}
              maxLength={500}
              placeholder="Nhập câu hỏi hoặc từ vựng bạn muốn tìm hiểu..."
              disabled={isQuizActive}
            />
          </div>
          <div className={styles.composerActions}>
            <button
              type="button"
              className={`${styles.button} ${styles.primary}`}
              onClick={sendMessage}
              disabled={isQuizActive || loading || !input.trim()}
            >
              {loading ? "Đang gửi..." : "Gửi ngay"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}


