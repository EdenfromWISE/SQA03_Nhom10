import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import './login.css';
import { getSavedTheme, toggleTheme } from '../theme';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import loginIllustration from '../assets/login-ilu.svg';

function LoginPage() {
    useDocumentTitle('Đăng nhập');
    // State để lưu trữ email và password người dùng nhập vào
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(getSavedTheme() === 'dark');
    useEffect(() => {
        // sync local state with global theme storage when component mounts
        setIsDarkMode(getSavedTheme() === 'dark');
    }, []);
    const navigate = useNavigate();

    // Hàm xử lý khi người dùng nhấn nút đăng nhập
    const handleSubmit = async (e) => {
        e.preventDefault(); // Ngăn trình duyệt reload lại trang
        try {
            const response = await axios.post(env.API_ENDPOINTS.AUTH.LOGIN, {
                email: email,
                password: password
            });

            // dj-rest-auth + JWT trả về 'access' và 'refresh'
            const accessToken = response?.data?.access || response?.data?.access_token || response?.data?.token || '';
            const refreshToken = response?.data?.refresh || '';

            if (!accessToken) throw new Error('Không nhận được access token');

            // Lưu token theo tuỳ chọn "Ghi nhớ đăng nhập"
            if (rememberMe) {
                localStorage.setItem('accessToken', accessToken);
                if (refreshToken) localStorage.setItem('refreshToken', refreshToken);
                localStorage.setItem('rememberMe', '1');
            } else {
                sessionStorage.setItem('accessToken', accessToken);
                if (refreshToken) sessionStorage.setItem('refreshToken', refreshToken);
                localStorage.removeItem('rememberMe');
                // KHÔNG XÓA accessToken/refreshToken ở localStorage ở đây, chỉ làm ở logout
            }

            // Điều hướng
            navigate('/');

        } catch (error) {
            console.error('Đăng nhập thất bại!', error);
            // Hiển thị thông báo lỗi từ backend
            const errorMessage = error.response?.data?.non_field_errors?.[0] || 
                               error.response?.data?.detail || 
                               error.response?.data?.error ||
                               'Email hoặc mật khẩu không đúng.';
            alert(errorMessage);
        }
    };

    // Hàm xử lý khi đăng nhập Google thành công (ID Token flow)
    // const handleGoogleSuccess = async (credentialResponse) => {
    //     try {
    //         const idToken = credentialResponse?.credential;
    //         if (!idToken) {
    //             alert('Không nhận được id_token từ Google');
    //             return;
    //         }

    //         const res = await fetch('http://localhost:8000/api/auth/google/id-token/', {
    //             method: 'POST',
    //             headers: { 'Content-Type': 'application/json' },
    //             body: JSON.stringify({ id_token: idToken }),
    //         });

    //         if (!res.ok) {
    //             const err = await res.json().catch(() => ({}));
    //             throw new Error(err.detail || 'Đăng nhập Google thất bại');
    //         }

    //         const data = await res.json();
    //         // Lưu token theo API mới
    //         if (data.access) localStorage.setItem('access_token', data.access);
    //         if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
    //         // Tương thích ngược với phần còn lại của app
    //         if (data.access) localStorage.setItem('accessToken', data.access);

    //         navigate('/');
    //     } catch (e) {
    //         console.error('Lỗi đăng nhập Google!', e);
    //         alert(e.message || 'Đã xảy ra lỗi khi đăng nhập bằng Google.');
    //     }
    // };

    const handleGoogleIdTokenSuccess = async (credentialResponse) => {
        try {
            const idToken = credentialResponse.credential;
            
            // 1. Gửi id_token đến endpoint MỚI
            const response = await axios.post(env.API_ENDPOINTS.AUTH.GOOGLE_ID_TOKEN, {
                id_token: idToken,
            });

            // 2. Lấy và lưu token của ứng dụng
            const accessToken = response.data.access;
            const refreshToken = response.data.refresh;

            localStorage.setItem('accessToken', accessToken);
            if (refreshToken) localStorage.setItem('refreshToken', refreshToken);

            navigate('/');

        } catch (error) {
            console.error('Lỗi đăng nhập Google!', error.response ? error.response.data : error);
            alert('Đã xảy ra lỗi khi đăng nhập bằng Google.');
        }
    };

    return (
        <div className={`login-container full-bleed ${isDarkMode ? 'dark' : ''}`}>
            {/* Left Side - Illustration */}
            <div className="illustration-side">
                <div className="illustration-content">
                    <div className="">
                        <img
                            src={loginIllustration}
                            alt="Illustration"
                            className="illustration-image"
                        />
                    </div>
                    <h1 className="brand-title">E-Vocab</h1>
                    <p className="brand-subtitle">Nâng cao vốn từ vựng của bạn với phương pháp học hiện đại</p>
                </div>
            </div>

            {/* Right Side - Login Form */}
            <div className="form-side">
                <div className="form-container">
                    {/* Dark Mode Toggle */}
                    <div className="dark-mode-toggle">
                        <button
                            type="button"
                            className="toggle-button"
                            onClick={() => setIsDarkMode(toggleTheme() === 'dark')}
                        >
                            {isDarkMode ? (
                                <svg className="toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                            ) : (
                                <svg className="toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                </svg>
                            )}
                        </button>
                    </div>

                    {/* Header */}
                    <div className="login-header">
                        <h2 className="login-title">Đăng nhập</h2>
                        <p className="login-subtitle">Chào mừng trở lại! Hãy đăng nhập để tiếp tục học tập</p>
                    </div>

                    {/* Social Login - Google */}
                    <div className="social-buttons">
                        <div className="google-login-container">
                            <GoogleLogin
                                onSuccess={handleGoogleIdTokenSuccess}
                                onError={() => alert('Đăng nhập Google thất bại')}
                                theme="outline"
                                size="large"
                                text="signin_with"
                                locale="vi"
                                width="360"
                            />
                        </div>
                    </div>

                    {/* Divider */}
                    <div className="divider">
                        <div className="divider-line"></div>
                        <div className="divider-text">
                            <span>hoặc</span>
                        </div>
                    </div>

                    {/* Form */}
                    <form className="form" onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="email" className="form-label">Email</label>
                            <input
                                id="email"
                                type="email"
                                placeholder="Nhập email của bạn"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="form-input"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password" className="form-label">Mật khẩu</label>
                            <div className="password-container">
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Nhập mật khẩu"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="form-input password-input"
                                    required
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? (
                                        <svg className="password-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                                        </svg>
                                    ) : (
                                        <svg className="password-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                        </svg>
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="form-controls">
                            <div className="checkbox-container">
                                <input
                                    type="checkbox"
                                    id="remember"
                                    checked={rememberMe}
                                    onChange={(e) => setRememberMe(e.target.checked)}
                                    className="checkbox"
                                />
                                <label htmlFor="remember" className="checkbox-label">Ghi nhớ đăng nhập</label>
                            </div>
                            <Link to="/forgot-password" className="forgot-password">Quên mật khẩu?</Link>
                        </div>

                        <button type="submit" className="submit-button">Đăng nhập</button>
                    </form>

                    {/* Sign Up Link */}
                    <div className="signup-link">
                        <span className="signup-text">Chưa có tài khoản? </span>
                        <Link to="/register" className="signup-button">Đăng ký ngay</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;