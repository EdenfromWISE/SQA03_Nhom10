import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './login.css';
import { getSavedTheme, toggleTheme } from '../theme';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

function ForgotPasswordPage() {
    useDocumentTitle('Quên mật khẩu');
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [sent, setSent] = useState(false);
    const [serverMsg, setServerMsg] = useState('');
    const [resetUrl, setResetUrl] = useState('');
    const [resetUid, setResetUid] = useState('');
    const [resetToken, setResetToken] = useState('');
    const [isDarkMode, setIsDarkMode] = useState(getSavedTheme() === 'dark');

    useEffect(() => {
        setIsDarkMode(getSavedTheme() === 'dark');
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!email) return;
        try {
            setLoading(true);
            setServerMsg('');
            const res = await axios.post(env.API_ENDPOINTS.AUTH.PASSWORD_RESET, { email });
            setSent(true);
            if (res?.data?.message) setServerMsg(res.data.message);
            if (res?.data?.reset_url) setResetUrl(res.data.reset_url);
            if (res?.data?.uid) setResetUid(res.data.uid);
            if (res?.data?.token) setResetToken(res.data.token);
        } catch (err) {
            setServerMsg('Đã xảy ra lỗi. Vui lòng thử lại.');
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
                    <div className="reset-icon">🔑</div>
                    <h2 className="login-title">Quên mật khẩu?</h2>
                    <p className="login-subtitle">Không sao! Nhập email đã đăng ký, chúng tôi sẽ gửi hướng dẫn đặt lại mật khẩu.</p>
                </div>

                {!sent ? (
                    <form className="form" onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="email" className="form-label">Địa chỉ email</label>
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

                        <button type="submit" className="submit-button" disabled={loading}>
                            {loading ? 'Đang gửi...' : 'Gửi email khôi phục'}
                        </button>

                        <div className="note-box">
                            <div className="note-title">Lưu ý quan trọng:</div>
                            <ul>
                                <li>Kiểm tra hộp thư đến của bạn</li>
                                <li>Kiểm tra mục Spam/Rác</li>
                                <li>Email có thể mất vài phút để đến</li>
                            </ul>
                        </div>
                    </form>
                ) : (
                    <div>
                        <div className="login-subtitle" style={{ marginBottom: '1rem' }}>
                            {serverMsg || 'Nếu email tồn tại, liên kết đặt lại đã được gửi.'}
                        </div>
                        <div className="note-box">
                            <div className="note-title">Lưu ý quan trọng:</div>
                            <ul>
                                <li>Kiểm tra hộp thư đến của bạn</li>
                                <li>Kiểm tra mục Spam/Rác</li>
                                <li>Email có thể mất vài phút để đến</li>
                            </ul>
                        </div>
                        {resetUrl ? (
                            <div className="note-box" style={{ marginTop: '1rem', background: '#ecfeff', borderColor: '#a5f3fc' }}>
                                <div className="note-title">Liên kết đặt lại (chỉ hiển thị khi DEV):</div>
                                <div style={{ wordBreak: 'break-all' }}>
                                    <a href={resetUrl} target="_blank" rel="noreferrer" className="forgot-password">{resetUrl}</a>
                                </div>
                                <div style={{ fontSize: '.8rem', marginTop: '.5rem', color: '#334155' }}>
                                    uid: <code>{resetUid}</code>
                                </div>
                                <div style={{ fontSize: '.8rem', color: '#334155' }}>
                                    token: <code>{resetToken}</code>
                                </div>
                                <div style={{ marginTop: '.5rem' }}>
                                    <Link to={`/reset-password?uid=${encodeURIComponent(resetUid)}&token=${encodeURIComponent(resetToken)}`} className="signup-button">Mở trang đặt lại mật khẩu trong app</Link>
                                </div>
                            </div>
                        ) : null}
                        <div style={{ marginTop: '1.25rem' }}>
                            <button className="signup-button" onClick={() => setSent(false)}>Gửi lại email khôi phục</button>
                        </div>
                    </div>
                )}

                <div className="signup-link">
                    <span className="signup-text">Bạn nhớ mật khẩu?</span>{' '}
                    <Link to="/login" className="signup-button">Đăng nhập ngay</Link>
                </div>
            </div>
        </div>
    );
}

export default ForgotPasswordPage;


