import React, { useEffect, useState } from 'react';
import styles from './Toast.module.css';

/**
 * Toast component để hiển thị thông báo dạng popup
 * @param {string} message - Nội dung thông báo
 * @param {string} type - Loại thông báo: 'success' | 'error' | 'info'
 * @param {boolean} show - Hiển thị hay không
 * @param {function} onClose - Callback khi đóng toast
 * @param {number} duration - Thời gian hiển thị (ms), mặc định 3000ms
 */
function Toast({ message, type = 'info', show = false, onClose, duration = 3000 }) {
    const [isVisible, setIsVisible] = useState(false);
    const [isExiting, setIsExiting] = useState(false);

    useEffect(() => {
        if (show && message) {
            setIsVisible(true);
            setIsExiting(false);
            
            const timer = setTimeout(() => {
                setIsExiting(true);
                setTimeout(() => {
                    setIsVisible(false);
                    if (onClose) onClose();
                }, 300); // Thời gian animation exit
            }, duration);

            return () => clearTimeout(timer);
        } else {
            setIsVisible(false);
            setIsExiting(false);
        }
    }, [show, message, duration, onClose]);

    if (!isVisible || !message) return null;

    return (
        <div 
            className={`${styles.toast} ${styles[type]} ${isExiting ? styles.exit : ''}`}
            onClick={() => {
                setIsExiting(true);
                setTimeout(() => {
                    setIsVisible(false);
                    if (onClose) onClose();
                }, 300);
            }}
        >
            <div className={styles.content}>
                <span className={styles.icon}>
                    {type === 'success' && '✓'}
                    {type === 'error' && '✕'}
                    {type === 'info' && 'ℹ'}
                </span>
                <span className={styles.message}>{message}</span>
            </div>
        </div>
    );
}

export default Toast;

