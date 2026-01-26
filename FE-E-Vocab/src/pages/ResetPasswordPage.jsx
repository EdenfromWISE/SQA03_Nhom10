import React, { useMemo, useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './login.css';
import { getSavedTheme, toggleTheme } from '../theme';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

function useQuery() {
    const { search } = useLocation();
    return useMemo(() => new URLSearchParams(search), [search]);
}

function ResetPasswordPage() {
    useDocumentTitle('Đặt lại mật khẩu');
    const query = useQuery();
    const navigate = useNavigate();
    const uid = query.get('uid') || '';
    const token = query.get('token') || '';

    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isDarkMode, setIsDarkMode] = useState(getSavedTheme() === 'dark');

    useEffect(() => {
        setIsDarkMode(getSavedTheme() === 'dark');
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        if (!uid || !token) {
            setError('Liên kết không hợp lệ. Thiếu uid hoặc token.');
            return;
        }
        if (password.length < 8) {
            setError('Mật khẩu tối thiểu 8 ký tự.');
            return;
        }
        if (password !== password2) {
            setError('Mật khẩu xác nhận không khớp.');
            return;
        }
        try {
            setLoading(true);
            await axios.post(env.API_ENDPOINTS.AUTH.PASSWORD_RESET_CONFIRM, {
                uid,
                token,
                new_password: password,
            });
            setMessage('Đặt lại mật khẩu thành công. Bạn có thể đăng nhập.');
            setTimeout(() => navigate('/login'), 1200);
        } catch (err) {
            setError(err?.response?.data?.error || 'Đặt lại mật khẩu thất bại.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`reset-page full-bleed ${isDarkMode ? 'dark' : ''}`}>
            <div className="reset-card">
                <div className="reset-back">
                    <Link to="/login" className="forgot-password">← Quay lại đăng nhập</Link>
                </div>

                <div className="login-header">
                    <div className="reset-icon">🔒</div>
                    <h2 className="login-title">Đặt lại mật khẩu</h2>
                    <p className="login-subtitle">Nhập mật khẩu mới cho tài khoản của bạn</p>
                </div>

                {error ? (
                    <div className="note-box" style={{ background: '#fef2f2', borderColor: '#fecaca', color: '#991b1b' }}>{error}</div>
                ) : null}
                {message ? (
                    <div className="note-box" style={{ background: '#ecfeff', borderColor: '#a5f3fc', color: '#075985' }}>{message}</div>
                ) : null}

                <form className="form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="password" className="form-label">Mật khẩu mới</label>
                        <input
                            id="password"
                            type="password"
                            placeholder="Nhập mật khẩu mới"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password2" className="form-label">Xác nhận mật khẩu</label>
                        <input
                            id="password2"
                            type="password"
                            placeholder="Nhập lại mật khẩu"
                            value={password2}
                            onChange={(e) => setPassword2(e.target.value)}
                            className="form-input"
                            required
                        />
                    </div>

                    <button type="submit" className="submit-button" disabled={loading}>
                        {loading ? 'Đang cập nhật...' : 'Cập nhật mật khẩu'}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ResetPasswordPage;


