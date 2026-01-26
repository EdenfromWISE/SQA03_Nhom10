import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Import các page
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CourseListPage from "./pages/CourseListPage";
import TopicListPage from "./pages/TopicListPage";
import VocabularyListPage from "./pages/VocabularyListPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
import ProfilePage from "./pages/ProfilePage";
import LearnFlashcardPage from "./pages/LearnFlashcardPage";
import PracticePageNew from "./pages/PracticePageNew";
import ReviewPage from "./pages/ReviewPage";
import ExamPage from "./pages/ExamPage";
import ChatbotPage from "./pages/ChatbotPage";
import LandingPage from "./pages/LandingPage";
import StatisticsPage from "./pages/StatisticsPage";
import SessionDetailPage from "./pages/SessionDetailPage";
// Import Layout
import Layout from "./Layout/Layout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Routes (không dùng Layout) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />

        {/* Routes có Layout (navigation sidebar) */}
        <Route element={<Layout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<LandingPage />} />
          <Route path="/course" element={<CourseListPage />} />
          <Route path="/course/:courseId" element={<TopicListPage />} />
          <Route path="/topic/:topicId" element={<VocabularyListPage />} />
          <Route path="/chatbot" element={<ChatbotPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/learn/:topicId" element={<LearnFlashcardPage />} />
          <Route path="/practice/:topicId" element={<PracticePageNew />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/exam/topic/:topicId" element={<ExamPage />} />
          <Route path="/stats" element={<StatisticsPage />} />
          <Route path="/session/:sessionId" element={<SessionDetailPage />} />
        </Route>

        {/* Nếu không khớp route nào thì redirect về Dashboard */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;