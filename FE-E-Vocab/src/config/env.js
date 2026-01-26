/**
 * Environment Configuration
 * Quản lý tất cả các biến môi trường của ứng dụng
 */

// Vite yêu cầu prefix VITE_ cho các biến môi trường
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

// Export các biến môi trường
export const env = {
  API_BASE_URL,
  GOOGLE_CLIENT_ID,
  
  // Các endpoint cụ thể
  API_ENDPOINTS: {
    AUTH: {
      LOGIN: `${API_BASE_URL}/auth/login/`,
      REGISTER: `${API_BASE_URL}/auth/registration/`,
      USER: `${API_BASE_URL}/auth/user/`,
      USER_UPDATE: `${API_BASE_URL}/auth/user/update/`,
      AVATAR_UPLOAD: `${API_BASE_URL}/auth/user/avatar/`,
      GOOGLE_ID_TOKEN: `${API_BASE_URL}/auth/google/id-token/`,
      PASSWORD_RESET: `${API_BASE_URL}/auth/password/reset/`,
      PASSWORD_RESET_CONFIRM: `${API_BASE_URL}/auth/password/reset/confirm/`,
      EMAIL_VERIFY_CONFIRM: `${API_BASE_URL}/auth/email/verify/confirm/`,
    },
    VOCABULARY: {
      COURSES: `${API_BASE_URL}/vocabulary/courses/`,
      COURSE_TOPICS: (courseId) => `${API_BASE_URL}/vocabulary/courses/${courseId}/`,
      TOPIC_VOCABULARY: (topicId) => `${API_BASE_URL}/vocabulary/topics/${topicId}/`,
      COURSE_FAVORITE: (courseId) => `${API_BASE_URL}/vocabulary/courses/${courseId}/favorite/`,
      SEARCH: `${API_BASE_URL}/vocabulary/vocabularies/search/`,
    },
    LEARNING: {
      BASE: `${API_BASE_URL}/learning`,
      SESSIONS: {
        PRACTICE: `${API_BASE_URL}/learning/sessions/practice/`,
        REVIEW: `${API_BASE_URL}/learning/sessions/review/`,
        EXAM: `${API_BASE_URL}/learning/sessions/exam/`,
        HISTORY: `${API_BASE_URL}/learning/sessions/history/`,
        DETAIL: (sessionId) => `${API_BASE_URL}/learning/sessions/${sessionId}/detail/`,
        QUESTIONS: (sessionId) => `${API_BASE_URL}/learning/sessions/${sessionId}/questions/`,
        SUBMIT_ANSWER: (sessionId) => `${API_BASE_URL}/learning/sessions/${sessionId}/submit-answer/`,
        COMPLETE: (sessionId) => `${API_BASE_URL}/learning/sessions/${sessionId}/complete/`,
        CANCEL: (sessionId) => `${API_BASE_URL}/learning/sessions/${sessionId}/cancel/`,
        GET: (sessionId) => `${API_BASE_URL}/learning/sessions/${sessionId}/`,
      },
      PRONUNCIATION: {
        ASSESS: `${API_BASE_URL}/learning/pronunciation/assess/`,
      },
    },
    PROGRESS: {
      BASE: `${API_BASE_URL}/progress`,
      STREAK: `${API_BASE_URL}/progress/streak/`,
      UPCOMING_REVIEW: `${API_BASE_URL}/progress/upcoming-review/`,
      OVERVIEW: `${API_BASE_URL}/progress/overview/`,
      DAILY_PROGRESS: `${API_BASE_URL}/progress/daily-progress/`,
      RECENT_SESSIONS: `${API_BASE_URL}/progress/recent-sessions/`,
    },
  },
};

export default env;

