// Layout.jsx
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import styles from "./Layout.module.css";
import { FaTachometerAlt, FaBook, FaChartBar, FaUser, FaCog, FaSignOutAlt, FaHome, FaSignInAlt, FaBars, FaTimes } from "react-icons/fa";
import { FaComments } from "react-icons/fa";
import openBookWhite from "../assets/open-book-white.png";
import { env } from "../config/env";

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [userAvatar, setUserAvatar] = useState(null);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    const loggedIn = !!token;
    setIsLoggedIn(loggedIn);
    
    // Hàm fetch user info
    const fetchUserInfo = async () => {
      if (!token) {
        setUserAvatar(null);
        setUserName('');
        return;
      }
      
      try {
        const res = await axios.get(env.API_ENDPOINTS.AUTH.USER_UPDATE, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setUserAvatar(res.data.avatar_url || null);
        // Lấy tên người dùng (ưu tiên first_name + last_name, nếu không có thì dùng username)
        const fullName = [res.data.last_name, res.data.first_name].filter(Boolean).join(' ');
        setUserName(fullName || res.data.username || res.data.email || '');
      } catch (error) {
        // Nếu lỗi, không làm gì cả, giữ giá trị mặc định
        console.error('Failed to fetch user info:', error);
      }
    };
    
    // Fetch user info nếu đã đăng nhập
    if (loggedIn) {
      fetchUserInfo();
    } else {
      setUserAvatar(null);
      setUserName('');
    }
  }, [location]);

  // Lắng nghe event khi avatar được cập nhật
  useEffect(() => {
    const handleAvatarUpdate = (event) => {
      // Cập nhật avatar từ event detail
      if (event.detail?.avatar_url) {
        setUserAvatar(event.detail.avatar_url);
      } else {
        // Nếu không có avatar_url trong event, refetch user info
        const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
        if (token) {
          axios.get(env.API_ENDPOINTS.AUTH.USER_UPDATE, {
            headers: { 'Authorization': `Bearer ${token}` }
          }).then(res => {
            setUserAvatar(res.data.avatar_url || null);
          }).catch(error => {
            console.error('Failed to fetch user info:', error);
          });
        }
      }
    };

    window.addEventListener('avatarUpdated', handleAvatarUpdate);
    return () => {
      window.removeEventListener('avatarUpdated', handleAvatarUpdate);
    };
  }, []);

  // Kiểm tra kích thước màn hình
  useEffect(() => {
    const checkMobile = () => {
      const width = window.innerWidth;
      const mobile = width < 768; // Mobile: < 768px
      setIsMobile(mobile);
      
      // Trên mobile (< 768px): sidebar ẩn hoàn toàn, cần bấm nút để mở
      // Trên tablet/desktop (>= 768px): sidebar luôn mở (có thể thu gọn trên tablet)
      if (mobile) {
        setIsSidebarOpen(false);
      } else {
        // Tablet/Desktop: luôn mở sidebar
        setIsSidebarOpen(true);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const menus = [
    { path: "/dashboard", label: "Trang chủ", icon: <FaHome /> },
    { path: "/course", label: "Học tập", icon: <FaBook /> },
    { path: "/chatbot", label: "Chatbot", icon: <FaComments /> },
    { path: "/stats", label: "Thống kê", icon: <FaChartBar /> },
    { path: "/profile", label: "Người dùng", icon: <FaUser /> },
  ];

  const handleAuthAction = () => {
    if (isLoggedIn) {
      localStorage.removeItem('accessToken');
      sessionStorage.removeItem('accessToken');
      setIsLoggedIn(false);
      navigate('/login');
    } else {
      navigate('/login');
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Đóng sidebar khi click vào menu item trên mobile
  const handleMenuClick = () => {
    if (isMobile) {
      setIsSidebarOpen(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Overlay cho mobile */}
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={toggleSidebar} />
      )}

      {/* Nút toggle sidebar (chỉ hiện trên mobile) */}
      {isMobile && (
        <button className={styles.menuToggle} onClick={toggleSidebar}>
          {isSidebarOpen ? <FaTimes /> : <FaBars />}
        </button>
      )}

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.sidebarOpen : styles.sidebarClosed} ${isMobile ? styles.sidebarMobile : ''}`}>
        {/* Logo + tên web */}
        <div className={styles.logo}>
          <img src={openBookWhite} alt="logo" className={styles.logoImg} />
          {isSidebarOpen && <span className={styles.logoText}>EVocab</span>}
        </div>
        {/* Navigation */}
        <nav className={styles.nav}>
          <ul>
            {menus.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={location.pathname === item.path ? styles.active : ""}
                  onClick={handleMenuClick}
                  title={!isSidebarOpen ? item.label : ''}
                >
                  <span className={styles.icon}>{item.icon}</span>
                  {isSidebarOpen && <span className={styles.text}>{item.label}</span>}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Nút đăng nhập/đăng xuất ở dưới */}
        <div className={styles.logout}>
          <button
            onClick={handleAuthAction}
            className={isLoggedIn ? styles.logoutButton : styles.loginButton}
            title={!isSidebarOpen ? (isLoggedIn ? "Đăng xuất" : "Đăng nhập") : (isLoggedIn ? userName || "Đăng xuất" : "Đăng nhập")}
          >
            {isLoggedIn ? (
              <>
                {userAvatar ? (
                  <img 
                    src={userAvatar} 
                    alt="Avatar" 
                    className={styles.avatarImg}
                  />
                ) : (
                  <div className={styles.avatarPlaceholder}>
                    {userName ? userName.charAt(0).toUpperCase() : <FaUser />}
                  </div>
                )}
                {isSidebarOpen && (
                  <span className={styles.text}>
                    {"Đăng xuất"}
                  </span>
                )}
              </>
            ) : (
              <>
                <span className={styles.icon}>
                  <FaSignInAlt />
                </span>
                {isSidebarOpen && (
                  <span className={styles.text}>
                    Đăng nhập
                  </span>
                )}
              </>
            )}
          </button>
        </div>
      </aside>

      {/* Nội dung */}
      <main className={`${styles.content} ${!isSidebarOpen && isMobile ? styles.contentFullWidth : ''}`}>
        <Outlet />
      </main>
    </div>
  );
}
