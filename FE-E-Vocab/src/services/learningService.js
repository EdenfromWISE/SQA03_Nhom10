/**
 * Learning Service - API calls cho learning và exam
 */

import axios from 'axios';
import { env } from '../config/env';

const API_BASE_URL = env.API_ENDPOINTS.LEARNING.BASE;

/**
 * Lấy token từ localStorage hoặc sessionStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
};

/**
 * Tạo headers với authorization token
 */
const getAuthHeaders = () => {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Tạo phiên luyện tập (practice session)
 * @param {number} topicId - ID của topic
 * @returns {Promise} Response chứa session_id và thông tin session
 */
export const createPracticeSession = async (topicId) => {
  const response = await axios.post(
    env.API_ENDPOINTS.LEARNING.SESSIONS.PRACTICE,
    { topic_id: topicId },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Tạo phiên ôn tập (review session) theo SRS
 * @param {object} options - Tùy chọn: total_questions
 * @returns {Promise} Response chứa session_id và thông tin session
 */
export const createReviewSession = async (options = {}) => {
  const response = await axios.post(
    env.API_ENDPOINTS.LEARNING.SESSIONS.REVIEW,
    { ...options },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Tạo phiên kiểm tra (exam session)
 * @param {number} topicId - ID của topic
 * @param {object} options - Tùy chọn: time_limit, total_questions, pass_score
 * @returns {Promise} Response chứa session_id và thông tin session
 */
export const createExamSession = async (topicId, options = {}) => {
  const response = await axios.post(
    env.API_ENDPOINTS.LEARNING.SESSIONS.EXAM,
    { 
      topic_id: topicId,
      ...options
    },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Lấy thông tin session
 * @param {number} sessionId - ID của session
 * @returns {Promise} Response chứa thông tin session
 */
export const getSession = async (sessionId) => {
  const response = await axios.get(
    env.API_ENDPOINTS.LEARNING.SESSIONS.GET(sessionId),
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Lấy chi tiết đầy đủ của session (bao gồm questions và user_answers)
 * @param {number} sessionId - ID của session
 * @returns {Promise} Response chứa chi tiết đầy đủ của session
 */
export const getSessionDetail = async (sessionId) => {
  const response = await axios.get(
    env.API_ENDPOINTS.LEARNING.SESSIONS.DETAIL(sessionId),
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Lấy danh sách câu hỏi của session
 * @param {number} sessionId - ID của session
 * @returns {Promise} Response chứa danh sách câu hỏi
 */
export const getSessionQuestions = async (sessionId) => {
  const response = await axios.get(
    env.API_ENDPOINTS.LEARNING.SESSIONS.QUESTIONS(sessionId),
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Gửi câu trả lời cho một câu hỏi
 * @param {number} sessionId - ID của session
 * @param {number} questionId - ID của câu hỏi
 * @param {any} answer - Câu trả lời (index, text, hoặc object)
 * @param {number} timeSpent - Thời gian làm bài (giây)
 * @param {number} pronunciationScore - Điểm phát âm (optional, cho speaking)
 * @returns {Promise} Response chứa kết quả đánh giá
 */
export const submitAnswer = async (sessionId, questionId, answer, timeSpent = 0, pronunciationScore = null) => {
  const payload = {
    question_id: questionId,
    answer: answer,
    time_spent: timeSpent
  };
  
  if (pronunciationScore !== null) {
    payload.pronunciation_score = pronunciationScore;
  }

  const response = await axios.post(
    env.API_ENDPOINTS.LEARNING.SESSIONS.SUBMIT_ANSWER(sessionId),
    payload,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Hoàn thành phiên học tập
 * @param {number} sessionId - ID của session
 * @returns {Promise} Response chứa kết quả tổng kết
 */
export const completeSession = async (sessionId) => {
  const response = await axios.post(
    env.API_ENDPOINTS.LEARNING.SESSIONS.COMPLETE(sessionId),
    {},
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Hủy phiên học tập
 * @param {number} sessionId - ID của session
 * @returns {Promise} Response message
 */
export const cancelSession = async (sessionId) => {
  const response = await axios.post(
    env.API_ENDPOINTS.LEARNING.SESSIONS.CANCEL(sessionId),
    {},
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Lấy lịch sử các phiên học tập
 * @param {string} mode - Loại session: practice, exam, hoặc null (tất cả)
 * @param {number} limit - Số lượng session tối đa
 * @returns {Promise} Response chứa danh sách sessions
 */
export const getSessionHistory = async (mode = null, limit = 20) => {
  const params = { limit };
  if (mode) {
    params.mode = mode;
  }

  const response = await axios.get(
    env.API_ENDPOINTS.LEARNING.SESSIONS.HISTORY,
    { 
      headers: getAuthHeaders(),
      params 
    }
  );
  return response.data;
};

/**
 * Đánh giá phát âm từ file audio
 * @param {Blob} audioBlob - File audio
 * @param {string} targetWord - Từ cần phát âm
 * @returns {Promise} Response chứa điểm và chi tiết phonemes
 */
export const assessPronunciation = async (audioBlob, targetWord) => {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'recording.webm');
  formData.append('word', targetWord);

  const response = await fetch(env.API_ENDPOINTS.LEARNING.PRONUNCIATION.ASSESS, {
    method: 'POST',
    headers: {
      ...getAuthHeaders()
    },
    body: formData
  });

  if (!response.ok) {
    throw new Error('Pronunciation assessment failed');
  }

  return await response.json();
};

export default {
  createPracticeSession,
  createReviewSession,
  createExamSession,
  getSession,
  getSessionDetail,
  getSessionQuestions,
  submitAnswer,
  completeSession,
  cancelSession,
  getSessionHistory,
  assessPronunciation
};

