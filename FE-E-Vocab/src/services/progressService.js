import axios from "axios";
import { env } from "../config/env";

const API_BASE_URL = env.API_ENDPOINTS.PROGRESS.BASE;

const getAuthToken = () =>
  localStorage.getItem("accessToken") || sessionStorage.getItem("accessToken");

const getAuthHeaders = () => {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const getStreakCalendar = async ({ year, month } = {}) => {
  const params = {};

  if (year) params.year = year;
  if (month) params.month = month;

  const response = await axios.get(env.API_ENDPOINTS.PROGRESS.STREAK, {
    headers: getAuthHeaders(),
    params,
  });

  return response.data;
};

export const getUpcomingReview = async (days = 7) => {
  const response = await axios.get(env.API_ENDPOINTS.PROGRESS.UPCOMING_REVIEW, {
    headers: getAuthHeaders(),
    params: { days },
  });

  return response.data;
};

export const getOverview = async () => {
  const response = await axios.get(env.API_ENDPOINTS.PROGRESS.OVERVIEW, {
    headers: getAuthHeaders(),
  });

  return response.data;
};

export const getDailyProgress = async () => {
  const response = await axios.get(env.API_ENDPOINTS.PROGRESS.DAILY_PROGRESS, {
    headers: getAuthHeaders(),
  });

  return response.data;
};

export const getRecentSessions = async (limit = 7) => {
  const response = await axios.get(env.API_ENDPOINTS.PROGRESS.RECENT_SESSIONS, {
    headers: getAuthHeaders(),
    params: { limit },
  });

  return response.data;
};

export default {
  getStreakCalendar,
  getUpcomingReview,
  getOverview,
  getDailyProgress,
  getRecentSessions,
};

