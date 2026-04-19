import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './login.css';
import { getSavedTheme, toggleTheme } from '../theme';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import loginIllustration from '../assets/login-ilu.svg';

function RegisterPage() {
    useDocumentTitle('Đăng ký');
    // State để lưu thông tin người dùng nhập
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState(''); // Để xác nhận mật khẩu
    const [showPassword, setShowPassword] = useState(false);
    const [showPassword2, setShowPassword2] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(getSavedTheme() === 'dark');
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState({});
    const [touched, setTouched] = useState({});
    
    useEffect(() => {
        setIsDarkMode(getSavedTheme() === 'dark');
    }, []);
    const navigate = useNavigate();

    // Validation functions
    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email) return 'Email là bắt buộc';
        if (!emailRegex.test(email)) return 'Email không hợp lệ';
        return '';
    };

    const validatePassword = (password) => {
        if (!password) return 'Mật khẩu là bắt buộc';
        if (password.length < 8) return 'Mật khẩu phải có ít nhất 8 ký tự';
        return '';
    };

    const validatePassword2 = (password2) => {
        if (!password2) return 'Vui lòng xác nhận mật khẩu';
        if (password2 !== password) return 'Mật khẩu không khớp';
        return '';
    };

    // Handle field blur for validation
    const handleBlur = (field) => {
        setTouched({ ...touched, [field]: true });
        let error = '';
        if (field === 'email') error = validateEmail(email);
        else if (field === 'password') error = validatePassword(password);
        else if (field === 'password2') error = validatePassword2(password2);
        setErrors({ ...errors, [field]: error });
    };

    // Handle field change
    const handleEmailChange = (e) => {
        setEmail(e.target.value);
        if (touched.email) {
            setErrors({ ...errors, email: validateEmail(e.target.value) });
        }
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
        if (touched.password) {
            setErrors({ ...errors, password: validatePassword(e.target.value) });
        }
        // Re-validate password2 if it's been touched
        if (touched.password2) {
            setErrors({ ...errors, password2: validatePassword2(password2) });
        }
    };

    const handlePassword2Change = (e) => {
        setPassword2(e.target.value);
        if (touched.password2) {
            setErrors({ ...errors, password2: validatePassword2(e.target.value) });
        }
    };

    // Hàm xử lý khi người dùng nhấn nút đăng ký
    const handleSubmit = async (e) => {
        e.preventDefault(); // Ngăn trình duyệt reload

        // Validate all fields
        const emailError = validateEmail(email);
        const passwordError = validatePassword(password);
        const password2Error = validatePassword2(password2);

        const newErrors = {
            email: emailError,
            password: passwordError,
            password2: password2Error
        };

        setErrors(newErrors);
        setTouched({ email: true, password: true, password2: true });

        // Nếu có lỗi, không submit
        if (emailError || passwordError || password2Error) {
            return;
        }

        setIsLoading(true);

        try {
            // Gửi thông tin đến API đăng ký của Django (chỉ email và password)
            const response = await axios.post(env.API_ENDPOINTS.AUTH.REGISTER, {
                email: email,
                username: email,  // Thêm dòng này
                password1: password,
                password2: password2
            });

            // Nếu thành công, hiển thị thông báo từ backend
            const successMessage = response.data?.message || response.data?.detail || 'Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.';
            alert(successMessage);
            navigate('/login');

        } catch (error) {
            console.error('Đăng ký thất bại!', error);
            // Hiển thị lỗi chi tiết nếu có
            const errorMessage = error.response?.data?.detail || 
                               error.response?.data?.email?.[0] || 
                               error.response?.data?.non_field_errors?.[0] ||
                               'Đăng ký thất bại. Vui lòng thử lại.';
            setErrors({ ...errors, submit: errorMessage });
        } finally {
            setIsLoading(false);
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
                    <p className="brand-subtitle">Tạo tài khoản để bắt đầu hành trình học từ vựng</p>
                </div>
            </div>

            {/* Right Side - Register Form */}
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
                        <h2 className="login-title">Đăng ký</h2>
                        <p className="login-subtitle">Tạo tài khoản mới để tiếp tục</p>
                    </div>

                    {/* Form */}
                    <form className="form" onSubmit={handleSubmit} noValidate>
                        {/* Error message from server */}
                        {errors.submit && (
                            <div className="error-message" style={{
                                padding: '12px',
                                marginBottom: '20px',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                borderRadius: '8px',
                                color: '#ef4444',
                                fontSize: '14px',
                                textAlign: 'center'
                            }}>
                                {errors.submit}
                            </div>
                        )}
                        <div className="form-group">
                            <label htmlFor="email" className="form-label">Email</label>
                            <input
                                id="email"
                                type="email"
                                placeholder="Nhập email của bạn"
                                value={email}
                                onChange={handleEmailChange}
                                onBlur={() => handleBlur('email')}
                                className={`form-input ${touched.email && errors.email ? 'form-input-error' : ''}`}
                                tabIndex={1}
                                autoFocus
                                autoComplete="email"
                                required
                            />
                            {touched.email && errors.email && (
                                <span className="error-text" style={{
                                    display: 'block',
                                    marginTop: '6px',
                                    fontSize: '13px',
                                    color: '#ef4444'
                                }}>{errors.email}</span>
                            )}
                        </div>

                        <div className="form-group">
                            <label htmlFor="password" className="form-label">Mật khẩu</label>
                            <div className="password-container">
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Nhập mật khẩu (tối thiểu 8 ký tự)"
                                    value={password}
                                    onChange={handlePasswordChange}
                                    onBlur={() => handleBlur('password')}
                                    className={`form-input password-input ${touched.password && errors.password ? 'form-input-error' : ''}`}
                                    tabIndex={2}
                                    autoComplete="new-password"
                                    required
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowPassword(!showPassword)}
                                    tabIndex={-1}
                                    aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
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
                            {touched.password && errors.password && (
                                <span className="error-text" style={{
                                    display: 'block',
                                    marginTop: '6px',
                                    fontSize: '13px',
                                    color: '#ef4444'
                                }}>{errors.password}</span>
                            )}
                        </div>

                        <div className="form-group">
                            <label htmlFor="password2" className="form-label">Xác nhận mật khẩu</label>
                            <div className="password-container">
                                <input
                                    id="password2"
                                    type={showPassword2 ? 'text' : 'password'}
                                    placeholder="Nhập lại mật khẩu"
                                    value={password2}
                                    onChange={handlePassword2Change}
                                    onBlur={() => handleBlur('password2')}
                                    className={`form-input password-input ${touched.password2 && errors.password2 ? 'form-input-error' : ''}`}
                                    tabIndex={3}
                                    autoComplete="new-password"
                                    required
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowPassword2(!showPassword2)}
                                    tabIndex={-1}
                                    aria-label={showPassword2 ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                                >
                                    {showPassword2 ? (
                                        <svg className="password-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                                        </svg>
                                    ) : (
                                        <svg className="password-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268-2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                        </svg>
                                    )}
                                </button>
                            </div>
                            {touched.password2 && errors.password2 && (
                                <span className="error-text" style={{
                                    display: 'block',
                                    marginTop: '6px',
                                    fontSize: '13px',
                                    color: '#ef4444'
                                }}>{errors.password2}</span>
                            )}
                        </div>

                        <button 
                            type="submit" 
                            className="submit-button" 
                            tabIndex={4}
                            disabled={isLoading}
                            style={{
                                opacity: isLoading ? 0.7 : 1,
                                cursor: isLoading ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {isLoading ? 'Đang xử lý...' : 'Đăng ký'}
                        </button>
                    </form>

                    {/* Sign In Link */}
                    <div className="signup-link">
                        <span className="signup-text">Đã có tài khoản? </span>
                        <Link to="/login" className="signup-button">Đăng nhập</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;