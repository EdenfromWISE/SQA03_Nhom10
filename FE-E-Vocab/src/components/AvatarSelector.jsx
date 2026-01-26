import React, { useRef } from 'react';
import styles from './AvatarSelector.module.css';
import profileStyles from '../pages/ProfilePage.module.css';

const AvatarSelector = ({ currentAvatar, onUpload }) => {
    const fileInputRef = useRef(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            alert('Vui lòng chọn file ảnh hợp lệ.');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            alert('Kích thước file không được vượt quá 5MB.');
            return;
        }
        onUpload(file);
    };

    const triggerFileUpload = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className={styles.avatarContainer}>
            <div className={styles.avatarWrapper}>
                {currentAvatar?.url ? (
                    <img 
                        src={currentAvatar.url} 
                        alt="Avatar" 
                        className={styles.avatarImage}
                    />
                ) : (
                    <div className={styles.avatarPlaceholder}>?</div>
                )}
            </div>
            <button 
                onClick={triggerFileUpload}
                className={`${profileStyles.primaryButton} ${styles.uploadButton}`}
            >
                Thay ảnh đại diện
            </button>
            <input 
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className={styles.hiddenInput}
            />
        </div>
    );
};

export default AvatarSelector;
