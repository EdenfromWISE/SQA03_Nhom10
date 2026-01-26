import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { env } from '../config/env';

function DashboardPage() {
    const [courses, setCourses] = useState([]);
    const [username, setUsername] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        // Hàm để lấy thông tin người dùng và các khóa học
        const fetchData = async () => {
            // Lấy token đã lưu từ localStorage
            const token = localStorage.getItem('accessToken');

            if (!token) {
                // Nếu không có token, người dùng chưa đăng nhập. Chuyển về trang login.
                navigate('/login');
                return;
            }

            try {
                // 1. Gửi request để lấy thông tin user (để chào mừng)
                const userResponse = await axios.get(env.API_ENDPOINTS.AUTH.USER, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setUsername(userResponse.data.username);

                // 2. Gửi request để lấy danh sách các khóa học
                const coursesResponse = await axios.get(env.API_ENDPOINTS.VOCABULARY.COURSES, {
                    headers: {
                        'Authorization': `Bearer ${token}` // Gửi token để xác thực
                    }
                });
                setCourses(coursesResponse.data);

            } catch (error) {
                console.error('Lỗi khi lấy dữ liệu!', error);
                // Nếu token hết hạn hoặc không hợp lệ, backend sẽ trả về lỗi 401
                // Xóa token cũ và chuyển về trang login
                localStorage.removeItem('accessToken');
                navigate('/login');
            }
        };

        fetchData();
    }, [navigate]); // useEffect sẽ chạy lại nếu navigate thay đổi

    // Hàm xử lý đăng xuất
    const handleLogout = () => {
        localStorage.removeItem('accessToken'); // Xóa token
        navigate('/login'); // Chuyển về trang login
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>Welcome, {username}!</h2>
                <button onClick={handleLogout}>Đăng xuất</button>
            </div>

            <h3>Danh sách khóa học từ vựng</h3>
            {courses.length > 0 ? (
                <ul>
                    {courses.map(course => (
                        <li key={course.id}>
                            <h4>{course.title}</h4>
                            <p>{course.description}</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>Chưa có khóa học nào.</p>
            )}
        </div>
    );
}

export default DashboardPage;