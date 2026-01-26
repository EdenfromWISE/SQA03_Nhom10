// TopicListPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from './TopicListPage.module.css';
import ContentCard from '../components/ContentCard/ContentCard';
import { env } from '../config/env';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

function TopicListPage() {
    useDocumentTitle('Chủ đề');
    const [course, setCourse] = useState(null);
    const { courseId } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
            if (!token) {
                navigate('/login');
                return;
            }
            try {
                const response = await axios.get(
                    env.API_ENDPOINTS.VOCABULARY.COURSE_TOPICS(courseId),
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                setCourse(response.data);
            } catch (error) {
                console.error("Error fetching course details", error);
                navigate('/');
            }
        };
        fetchData();
    }, [courseId, navigate]);

    if (!course)
        return <div className={styles.loading}>Đang tải danh sách chủ đề...</div>;

    // Tính tiến độ
    const totalTopics = course.topics?.length || 0;
    const completedTopics = course.topics?.filter(t => t.is_passed).length || 0;
    const progressPercentage = totalTopics > 0 ? (completedTopics / totalTopics) * 100 : 0;

    return (
        <div className={styles.topicPage}>
            <button 
                className={styles.backBtn}
                onClick={() => navigate(`/course`)}
            >
                ← Quay lại
            </button>
            {/* <h1 className={styles.courseTitle}>{course.title}</h1> */}
            
            {/* Progress Section */}
            <div className={styles.progressSection}>
                <div className={styles.progressInfo}>
                    <span className={styles.progressText}>
                        Đã hoàn thành: <strong>{completedTopics}/{totalTopics}</strong> chủ đề trong khóa học <strong>{course.title}</strong>
                    </span>
                </div>
                <div className={styles.progressBarContainer}>
                    <div 
                        className={styles.progressBar}
                        style={{ width: `${progressPercentage}%` }}
                    />
                </div>
            </div>
            
            {/* <hr className={styles.divider} /> */}

            <div className={styles.topicList}>
                {course.topics?.map(topic => {
                    const vocabCount = topic.word_count ?? 0;
                    // Chuyển is_passed thành progressStatus
                    const topicProgressStatus = topic.is_passed ? "completed" : null;

                    return (
                        <ContentCard
                            key={topic.id}
                            to={`/topic/${topic.id}`}
                            imageUrl={topic.image_url}
                            title={topic.title}
                            meta={`${vocabCount} từ vựng`}
                            showFavorite={false}
                            progressStatus={topicProgressStatus}
                        />
                    );
                })}
            </div>
        </div>
    );
}

export default TopicListPage;
