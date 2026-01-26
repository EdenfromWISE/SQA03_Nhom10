import React, { useEffect, useMemo, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AvatarSelector from '../components/AvatarSelector';
import Toast from '../components/Toast';
import styles from './ProfilePage.module.css';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

function ProfilePage() {
    useDocumentTitle('Hồ sơ');
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    // Toast state
    const [toast, setToast] = useState({ show: false, message: '', type: 'info' });
    const [editForm, setEditForm] = useState({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
    });
    const [age, setAge] = useState('');
    const [avatarUrl, setAvatarUrl] = useState(null);
    const [passwordForm, setPasswordForm] = useState({
        current: '',
        next: '',
        confirm: '',
    });

    // Cài đặt thông báo (di chuyển từ trang Cài đặt sang)
    const [notifications, setNotifications] = useState({
        email: true,
        studyTips: false,
        examReminders: true,
        productUpdates: false,
    });
    const [savingNotifications, setSavingNotifications] = useState(false);
    const notificationSaveTimeoutRef = useRef(null);

    // Danger zone: xóa tài khoản (di chuyển từ trang Cài đặt sang)
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deletePassword, setDeletePassword] = useState('');
    const [deleteWarning, setDeleteWarning] = useState('');
    const [deleteSuccess, setDeleteSuccess] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
        if (!token) {
            navigate('/login');
            return;
        }
        const fetchUser = async () => {
            try {
                // Sử dụng endpoint USER_UPDATE để lấy thông tin đầy đủ (bao gồm age)
                const res = await axios.get(env.API_ENDPOINTS.AUTH.USER_UPDATE, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setUser(res.data);
                setEditForm({
                    first_name: res.data.first_name || '',
                    last_name: res.data.last_name || '',
                    username: res.data.username || '',
                    email: res.data.email || ''
                });
                // Load age từ backend response
                setAge(res.data.age || '');
                // Load avatar URL từ backend response
                setAvatarUrl(res.data.avatar_url || null);
                // Load cài đặt thông báo từ backend response
                setNotifications({
                    email: res.data.notification_email !== undefined ? res.data.notification_email : true,
                    studyTips: res.data.notification_study_tips !== undefined ? res.data.notification_study_tips : false,
                    examReminders: res.data.notification_exam_reminders !== undefined ? res.data.notification_exam_reminders : true,
                    productUpdates: res.data.notification_product_updates !== undefined ? res.data.notification_product_updates : false,
                });
            } catch (e) {
                showToast('Không thể tải thông tin người dùng.', 'error');
                if (e?.response?.status === 401) navigate('/login');
            } finally {
                setLoading(false);
            }
        };
        fetchUser();
    }, [navigate]);

    // Helper function để hiển thị toast
    const showToast = (message, type = 'info') => {
        setToast({ show: true, message, type });
    };

    // Xử lý upload avatar lên backend
    const handleAvatarUpload = async (file) => {
        // Validation
        if (!file.type.startsWith('image/')) {
            showToast('Vui lòng chọn file ảnh hợp lệ.', 'error');
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            showToast('Kích thước file không được vượt quá 5MB.', 'error');
            return;
        }
        
        try {
            const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
            const formData = new FormData();
            formData.append('avatar', file);
            
            const res = await axios.post(env.API_ENDPOINTS.AUTH.AVATAR_UPLOAD, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            
            setAvatarUrl(res.data.avatar_url);
            showToast('Đã cập nhật ảnh đại diện!', 'success');
            
            // Dispatch event để Layout cập nhật avatar
            window.dispatchEvent(new CustomEvent('avatarUpdated', {
                detail: { avatar_url: res.data.avatar_url }
            }));
        } catch (e) {
            if (e?.response?.status === 400) {
                const errorMsg = e?.response?.data?.error || 'Không thể upload avatar.';
                showToast(errorMsg, 'error');
            } else if (e?.response?.status === 401) {
                showToast('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'error');
                setTimeout(() => navigate('/login'), 1500);
            } else {
                showToast('Không thể upload avatar.', 'error');
            }
        }
    };

    const handleEdit = () => {
        setIsEditing(true);
    };
    const handleCancel = () => {
        setIsEditing(false);
        setEditForm({
            first_name: user?.first_name || '',
            last_name: user?.last_name || '',
            username: user?.username || '',
            email: user?.email || ''
        });
        setAge(user?.age || '');
    };

    const handleSave = async () => {
        // Validation
        if (!editForm.username || editForm.username.trim() === '') {
            showToast('Tên đăng nhập không được để trống.', 'error');
            return;
        }
        
        if (age && (isNaN(age) || parseInt(age) < 1 || parseInt(age) > 150)) {
            showToast('Tuổi phải là số từ 1 đến 150.', 'error');
            return;
        }
        
        try {
            const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
            const payload = {
                username: editForm.username.trim(),
                first_name: editForm.first_name.trim(),
                last_name: editForm.last_name.trim(),
            };
            
            // Chỉ gửi age nếu có giá trị
            if (age && age.trim() !== '') {
                payload.age = parseInt(age);
            } else {
                payload.age = null;
            }
            
            const res = await axios.patch(env.API_ENDPOINTS.AUTH.USER_UPDATE, payload, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setUser(res.data);
            setIsEditing(false);
            // Cập nhật age từ response
            setAge(res.data.age || '');
            showToast('Cập nhật thông tin thành công!', 'success');
        } catch (e) {
            if (e?.response?.status === 400) {
                // Xử lý các lỗi validation từ backend
                const errorData = e?.response?.data;
                let errorMsg = 'Dữ liệu không hợp lệ.';
                if (errorData?.username) {
                    errorMsg = Array.isArray(errorData.username) ? errorData.username[0] : errorData.username;
                } else if (errorData?.age) {
                    errorMsg = Array.isArray(errorData.age) ? errorData.age[0] : errorData.age;
                } else if (errorData?.non_field_errors) {
                    errorMsg = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors;
                }
                showToast(errorMsg, 'error');
            } else if (e?.response?.status === 401) {
                showToast('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'error');
                setTimeout(() => navigate('/login'), 1500);
            } else {
                showToast('Không thể cập nhật thông tin.', 'error');
            }
        }
    };

    const handlePasswordSave = () => {
        if (!passwordForm.current || !passwordForm.next || !passwordForm.confirm) {
            showToast('Vui lòng nhập đầy đủ thông tin mật khẩu.', 'error');
            return;
        }
        if (passwordForm.next !== passwordForm.confirm) {
            showToast('Mật khẩu mới và xác nhận không khớp.', 'error');
            return;
        }
        showToast('Tính năng đổi mật khẩu đang được phát triển, vui lòng thử lại sau.', 'info');
        setPasswordForm({ current: '', next: '', confirm: '' });
    };

    const handlePasswordCancel = () => {
        setPasswordForm({ current: '', next: '', confirm: '' });
    };

    const passwordDirty = useMemo(
        () => Boolean(passwordForm.current || passwordForm.next || passwordForm.confirm),
        [passwordForm]
    );

    // Logic thông báo - auto-save với debounce
    const toggleNotification = async (key) => {
        const newValue = !notifications[key];
        setNotifications((prev) => {
            const updated = { ...prev, [key]: newValue };
            
            // Clear timeout cũ nếu có
            if (notificationSaveTimeoutRef.current) {
                clearTimeout(notificationSaveTimeoutRef.current);
            }
            
            // Set timeout để auto-save sau 500ms
            notificationSaveTimeoutRef.current = setTimeout(async () => {
                await saveNotifications(updated);
            }, 1000);
            
            return updated;
        });
    };

    // Hàm lưu cài đặt thông báo
    const saveNotifications = async (notificationsToSave = null) => {
        const notificationsData = notificationsToSave || notifications;
        setSavingNotifications(true);
        
        try {
            const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
            const payload = {
                notification_email: notificationsData.email,
                notification_study_tips: notificationsData.studyTips,
                notification_exam_reminders: notificationsData.examReminders,
                notification_product_updates: notificationsData.productUpdates,
            };
            
            await axios.patch(env.API_ENDPOINTS.AUTH.USER_UPDATE, payload, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            showToast('Đã cập nhật cài đặt thông báo!', 'success');
        } catch (e) {
            if (e?.response?.status === 401) {
                showToast('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'error');
                setTimeout(() => navigate('/login'), 1500);
            } else {
                showToast('Không thể cập nhật cài đặt thông báo.', 'error');
                // Revert lại giá trị cũ nếu lỗi
                const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
                try {
                    const res = await axios.get(env.API_ENDPOINTS.AUTH.USER_UPDATE, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    setNotifications({
                        email: res.data.notification_email !== undefined ? res.data.notification_email : true,
                        studyTips: res.data.notification_study_tips !== undefined ? res.data.notification_study_tips : false,
                        examReminders: res.data.notification_exam_reminders !== undefined ? res.data.notification_exam_reminders : true,
                        productUpdates: res.data.notification_product_updates !== undefined ? res.data.notification_product_updates : false,
                    });
                } catch {
                    // Nếu không fetch được, giữ nguyên giá trị hiện tại
                }
            }
        } finally {
            setSavingNotifications(false);
        }
    };

    // Logic Danger Zone
    const deletePasswordValid = useMemo(
        () => deletePassword.trim() === '123456',
        [deletePassword]
    );

    const handleDeleteRequest = () => {
        setDeleteWarning('');
        setDeleteSuccess(false);
        if (!deletePasswordValid) {
            setDeleteWarning('Mật khẩu chưa chính xác. Vui lòng thử lại.');
            return;
        }
        setDeleteWarning(
            'Tài khoản của bạn sẽ bị xóa vĩnh viễn trong 7 ngày tới. Bạn có chắc chắn muốn tiếp tục?'
        );
        setDeleteSuccess(true);
    };

    const resetDangerZone = () => {
        setDeletePassword('');
        setDeleteWarning('');
        setDeleteSuccess(false);
        setShowDeleteConfirm(false);
    };

    // Cleanup timeout khi component unmount
    useEffect(() => {
        return () => {
            if (notificationSaveTimeoutRef.current) {
                clearTimeout(notificationSaveTimeoutRef.current);
            }
        };
    }, []);

    return (
        <div className={styles.page}>
            <div className={styles.container}>
                <div className={styles.hero}>
                    <div>
                        <h1>Hồ sơ người dùng</h1>
                        <p>Quản lý thông tin cá nhân, bảo mật và cài đặt của bạn.</p>
                    </div>
                </div>

                {loading && <div className={styles.loadingCard}>Đang tải hồ sơ...</div>}

                {!loading && user && (
                    <div className={styles.grid}>
                        <section className={styles.card}>
                            <div className={styles.cardHeader}>
                                <div>
                                    <h2 className={styles.cardTitle}>Thông tin cá nhân</h2>
                                </div>
                                <span className={styles.tag}>Hồ sơ</span>
                            </div>
                            
                            <div className={styles.profileContent}>
                                <div className={styles.avatarSection}>
                                    <AvatarSelector currentAvatar={avatarUrl ? { url: avatarUrl } : null} onUpload={handleAvatarUpload} />
                                </div>
                                
                                <div className={styles.infoSection}>
                                    <div className={styles.infoList}>
                                        <div className={styles.infoRow}>
                                            <span className={styles.label}>Email</span>
                                            <span className={styles.value}>{user?.email || '—'}</span>
                                        </div>
                                        <div className={styles.infoRow}>
                                            <span className={styles.label}>Họ và tên</span>
                                            {isEditing ? (
                                                <div className={styles.formGrid}>
                                                    <input
                                                        className={styles.input}
                                                        type="text"
                                                        value={editForm.last_name}
                                                        onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                                                        placeholder="Họ"
                                                    />
                                                    <input
                                                        className={styles.input}
                                                        type="text"
                                                        value={editForm.first_name}
                                                        onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                                                        placeholder="Tên"
                                                    />
                                                </div>
                                            ) : (
                                                <span className={styles.value}>
                                                    {[user?.last_name, user?.first_name].filter(Boolean).join(' ') || '—'}
                                                </span>
                                            )}
                                        </div>
                                        <div className={styles.infoRow}>
                                            <span className={styles.label}>Tuổi</span>
                                            {isEditing ? (
                                                <input
                                                    className={styles.input}
                                                    type="number"
                                                    min="1"
                                                    max="150"
                                                    value={age}
                                                    onChange={(e) => setAge(e.target.value)}
                                                    placeholder="Nhập tuổi của bạn"
                                                />
                                            ) : (
                                                <span className={styles.value}>{age || '—'}</span>
                                            )}
                                        </div>
                                        <div className={styles.infoRow}>
                                            <span className={styles.label}>Tên đăng nhập</span>
                                            {isEditing ? (
                                                <input
                                                    className={styles.input}
                                                    type="text"
                                                    value={editForm.username}
                                                    onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                                                    placeholder="Nhập tên đăng nhập"
                                                />
                                            ) : (
                                                <span className={styles.value}>{user?.username || '—'}</span>
                                            )}
                                        </div>
                                    </div>
                                    
                                    <div className={styles.profileActions}>
                                        {!isEditing && (
                                            <button onClick={handleEdit} className={styles.primaryButton} disabled={loading || !user}>
                                                Chỉnh sửa thông tin
                                            </button>
                                        )}
                                        {isEditing && (
                                            <>
                                                <button onClick={handleSave} className={styles.primaryButton}>Lưu thay đổi</button>
                                                <button onClick={handleCancel} className={styles.secondaryButton}>Hủy</button>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Tài khoản & Mật khẩu */}
                        <section className={styles.card}>
                            <div className={styles.cardHeader}>
                                <div>
                                    <h2 className={styles.cardTitle}>Thay đổi mật khẩu</h2>
                                </div>
                                <span className={styles.tag}>Mật khẩu</span>
                            </div>
                            <div className={styles.passwordSection}>
                                <div className={styles.inputGroup}>
                                    <label htmlFor="current-password">Mật khẩu hiện tại</label>
                                    <input
                                        id="current-password"
                                        className={styles.input}
                                        type="password"
                                        placeholder="••••••••"
                                        value={passwordForm.current}
                                        onChange={(e) => setPasswordForm({ ...passwordForm, current: e.target.value })}
                                    />
                                </div>
                                <div className={styles.inputGroup}>
                                    <label htmlFor="new-password">Mật khẩu mới</label>
                                    <input
                                        id="new-password"
                                        className={styles.input}
                                        type="password"
                                        placeholder="••••••••"
                                        value={passwordForm.next}
                                        onChange={(e) => setPasswordForm({ ...passwordForm, next: e.target.value })}
                                    />
                                </div>
                                <div className={styles.inputGroup}>
                                    <label htmlFor="confirm-password">Xác nhận mật khẩu mới</label>
                                    <input
                                        id="confirm-password"
                                        className={styles.input}
                                        type="password"
                                        placeholder="••••••••"
                                        value={passwordForm.confirm}
                                        onChange={(e) => setPasswordForm({ ...passwordForm, confirm: e.target.value })}
                                    />
                                </div>
                                <div className={styles.passwordActions}>
                                    <button className={styles.primaryButton} onClick={handlePasswordSave}>
                                        Lưu thay đổi mật khẩu
                                    </button>
                                    {passwordDirty && (
                                        <button className={styles.secondaryButton} onClick={handlePasswordCancel}>
                                            Hủy
                                        </button>
                                    )}
                                </div>
                            </div>
                        </section>

                        {/* Cài đặt khác */}
                        <section className={styles.card}>
                            <div className={styles.cardHeader}>
                                <div>
                                    <h2 className={styles.cardTitle}>Cài đặt khác</h2>
                                </div>
                                <span className={styles.tag}>Cài đặt</span>
                            </div>
                            <div className={styles.infoList}>
                                {[
                                    {
                                        key: 'email',
                                        title: 'Email hàng tuần',
                                        subtitle: 'Tổng hợp hoạt động học tập và cập nhật mới',
                                    },
                                    {
                                        key: 'studyTips',
                                        title: 'Gợi ý học tập',
                                        subtitle: 'Gợi ý flashcard và khóa học theo tiến độ',
                                    },
                                    {
                                        key: 'examReminders',
                                        title: 'Nhắc lịch kiểm tra',
                                        subtitle: 'Nhận thông báo khi tới ngày làm bài kiểm tra',
                                    },
                                    {
                                        key: 'productUpdates',
                                        title: 'Thông báo sản phẩm',
                                        subtitle: 'Thông tin về tính năng và chương trình mới',
                                    },
                                ].map((item) => (
                                    <div key={item.key} className={styles.infoRow}>
                                        <span className={styles.label}>{item.title}</span>
                                        <div className={styles.notificationRow}>
                                            <span className={styles.valueSmall}>{item.subtitle}</span>
                                            <label>
                                                <input
                                                    type="checkbox"
                                                    checked={notifications[item.key]}
                                                    onChange={() => toggleNotification(item.key)}
                                                    disabled={savingNotifications}
                                                />{' '}
                                                Bật
                                            </label>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            
                            {/* Danger Zone: Xóa tài khoản */}
                            <div className={styles.dangerZone}>
                                <div className={styles.dangerZoneHeader}>
                                    <h3 className={styles.dangerZoneTitle}>Xóa tài khoản</h3>
                                    <p className={styles.dangerZoneSubtitle}>
                                        Xóa vĩnh viễn tài khoản và toàn bộ dữ liệu liên quan.
                                    </p>
                                </div>
                                <div className={styles.passwordSection}>
                                    {!showDeleteConfirm ? (
                                        <button
                                            className={styles.dangerButton}
                                            onClick={() => setShowDeleteConfirm(true)}
                                        >
                                            Xóa tài khoản
                                        </button>
                                    ) : (
                                        <>
                                            <div className={styles.inputGroup}>
                                                <label htmlFor="delete-password">Nhập mật khẩu của bạn</label>
                                                <input
                                                    id="delete-password"
                                                    className={styles.input}
                                                    type="password"
                                                    placeholder="••••••••"
                                                    value={deletePassword}
                                                    onChange={(e) => setDeletePassword(e.target.value)}
                                                />
                                            </div>
                                            {deleteWarning && (
                                                <div className={`${styles.statusMessage} ${styles.error}`}>
                                                    {deleteWarning}
                                                </div>
                                            )}
                                            {deleteSuccess && deletePasswordValid && (
                                                <div className={`${styles.statusMessage} ${styles.success}`}>
                                                    Tài khoản của bạn đã được đưa vào hàng chờ xóa.
                                                </div>
                                            )}
                                            <div className={styles.passwordActions}>
                                                <button
                                                    className={styles.dangerButton}
                                                    onClick={handleDeleteRequest}
                                                >
                                                    Xác nhận xóa
                                                </button>
                                                <button
                                                    className={styles.secondaryButton}
                                                    onClick={resetDangerZone}
                                                >
                                                    Hủy bỏ
                                                </button>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                        </section>
                    </div>
                )}
            </div>
            
            {/* Toast Notification */}
            <Toast
                message={toast.message}
                type={toast.type}
                show={toast.show}
                onClose={() => setToast({ show: false, message: '', type: 'info' })}
                duration={3000}
            />
        </div>
    );
}

export default ProfilePage;


