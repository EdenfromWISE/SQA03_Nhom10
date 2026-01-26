import React, { useMemo, useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './VerifyEmail.css'; // Dùng file CSS mới này hoặc gộp vào login.css
import { getSavedTheme } from '../theme';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import loginIllustration from '../assets/login-ilu.svg';

// --- Icon Components (Inline SVG - Không cần thư viện) ---
const SpinnerIcon = () => (
  <svg className="animate-spin" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

const SuccessIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

const ErrorIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="15" y1="9" x2="9" y2="15" />
    <line x1="9" y1="9" x2="15" y2="15" />
  </svg>
);

const ArrowRightIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 8 }}>
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const MailIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2" />
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
);

// --- Main Component ---
function useQuery() {
  const { search } = useLocation();
  return useMemo(() => new URLSearchParams(search), [search]);
}

function VerifyEmailPage() {
  useDocumentTitle('Xác thực email | E-Vocab');
  const query = useQuery();
  const navigate = useNavigate();
  const uid = query.get('uid') || '';
  const token = query.get('token') || '';

  const [status, setStatus] = useState('loading'); // 'loading', 'success', 'error'
  const [message, setMessage] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(getSavedTheme() === 'dark');

  useEffect(() => {
    setIsDarkMode(getSavedTheme() === 'dark');
  }, []);

  useEffect(() => {
    const verifyEmail = async () => {
      if (!uid || !token) {
        setStatus('error');
        setMessage('Liên kết xác thực không hợp lệ hoặc thiếu thông tin.');
        return;
      }

      try {
        const response = await axios.post(
          env.API_ENDPOINTS.AUTH.EMAIL_VERIFY_CONFIRM,
          { uid, token }
        );
        setStatus('success');
        setMessage(
          response.data?.message ||
            'Tài khoản của bạn đã được kích hoạt thành công.'
        );
        // Tự động chuyển trang sau 4s
        setTimeout(() => navigate('/login'), 4000);
      } catch (err) {
        setStatus('error');
        setMessage(
          err?.response?.data?.error ||
            'Liên kết xác thực đã hết hạn hoặc không tồn tại.'
        );
      }
    };

    // Giả lập delay nhỏ 1s để UX mượt hơn (tránh chớp nháy nếu mạng quá nhanh)
    const timer = setTimeout(() => verifyEmail(), 1000);
    return () => clearTimeout(timer);
  }, [uid, token, navigate]);

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="verify-content fade-in">
            <div className="icon-wrapper icon-loading">
              <SpinnerIcon />
            </div>
            <h2 className="verify-title">Đang xác thực...</h2>
            <p className="verify-desc">
              Hệ thống đang kiểm tra thông tin của bạn. <br/>Vui lòng đợi trong giây lát.
            </p>
          </div>
        );

      case 'success':
        return (
          <div className="verify-content fade-in">
            <div className="icon-wrapper icon-success">
              <SuccessIcon />
            </div>
            <h2 className="verify-title text-success">Thành công!</h2>
            <p className="verify-desc">{message}</p>
            <div className="verify-actions">
              <p className="redirect-hint">Đang chuyển hướng về trang đăng nhập...</p>
              <Link to="/login" className="btn-verify btn-primary">
                Đăng nhập ngay <ArrowRightIcon />
              </Link>
            </div>
          </div>
        );

      case 'error':
        return (
          <div className="verify-content fade-in">
            <div className="icon-wrapper icon-error">
              <ErrorIcon />
            </div>
            <h2 className="verify-title text-error">Xác thực thất bại</h2>
            <p className="verify-desc">{message}</p>
            <div className="verify-actions">
              <Link to="/login" className="btn-verify btn-outline">
                Quay lại đăng nhập
              </Link>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`login-container full-bleed ${isDarkMode ? 'dark' : ''}`}>
      {/* Left Side */}
      <div className="illustration-side">
        <div className="illustration-content">
          <img
            src={loginIllustration}
            alt="Verify Email"
            className="illustration-image"
          />
          <h1 className="brand-title">E-Vocab</h1>
          <p className="brand-subtitle">
            Học từ vựng tiếng Anh thông minh và hiệu quả hơn mỗi ngày.
          </p>
        </div>
      </div>

      {/* Right Side */}
      <div className="form-side">
        <div className="verify-card-container">
          {/* Decorative Header Icon */}
          <div className="verify-header-icon">
            <MailIcon />
          </div>
          
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default VerifyEmailPage;