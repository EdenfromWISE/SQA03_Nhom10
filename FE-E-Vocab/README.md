# Language Learning Platform - Frontend
.
Ứng dụng học ngôn ngữ được xây dựng bằng React với các tính năng quản lý khóa học, chủ đề và từ vựng.

## 🚀 Tính năng

- **Đăng nhập/Đăng ký**: Xác thực người dùng với Google OAuth
- **Quản lý khóa học**: Hiển thị danh sách các khóa học
- **Quản lý chủ đề**: Xem các chủ đề trong từng khóa học
- **Quản lý từ vựng**: Học từ vựng theo từng chủ đề
- **Responsive Design**: Giao diện thân thiện trên mọi thiết bị

## 📋 Yêu cầu hệ thống

- Node.js >= 16.0.0
- npm >= 8.0.0

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd my-frontend
```

### 2. Cài đặt dependencies
```bash
npm install
```

### 3. Chạy ứng dụng
```bash
npm run dev
```

Ứng dụng sẽ chạy tại `http://localhost:5173`

## 📦 Dependencies chính

### Production Dependencies
- **React 19.1.1**: Framework UI chính
- **React Router DOM 7.9.1**: Điều hướng trang
- **Axios 1.12.2**: HTTP client
- **@react-oauth/google 0.12.2**: Xác thực Google

### Development Dependencies
- **Vite 7.1.6**: Build tool và dev server
- **ESLint 9.35.0**: Code linting
- **TypeScript types**: Type definitions cho React

## 🎯 Scripts có sẵn

```bash
# Chạy development server
npm run dev

# Build cho production
npm run build

# Chạy linter
npm run lint

# Preview production build
npm run preview
```

## 📁 Cấu trúc thư mục

```
src/
├── pages/                 # Các trang chính
│   ├── LoginPage.jsx      # Trang đăng nhập
│   ├── RegisterPage.jsx   # Trang đăng ký
│   ├── CourseListPage.jsx # Danh sách khóa học
│   ├── TopicListPage.jsx  # Danh sách chủ đề
│   ├── VocabularyListPage.jsx # Danh sách từ vựng
│   └── DashboardPage.jsx  # Trang dashboard
├── App.jsx               # Component chính
├── main.jsx             # Entry point
└── assets/              # Tài nguyên tĩnh
```

## 🔧 Cấu hình

### Environment Variables
Tạo file `.env` trong thư mục root với các biến sau (hoặc copy từ `.env.example`):

```env
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8000/api

# Google OAuth Configuration
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here

# Development Server Proxy (for vite.config.js)
VITE_PROXY_TARGET=http://localhost:8000
```

**Lưu ý:** 
- Vite yêu cầu prefix `VITE_` cho tất cả các biến môi trường
- File `.env` đã được thêm vào `.gitignore` để tránh commit nhầm thông tin nhạy cảm
- Copy file `.env.example` và đổi tên thành `.env`, sau đó điền các giá trị phù hợp

### Google OAuth Setup
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Kích hoạt Google+ API
4. Tạo OAuth 2.0 credentials
5. Thêm domain vào authorized origins

## 🚀 Deployment

### Build cho production
```bash
npm run build
```

### Deploy lên Vercel
```bash
npm install -g vercel
vercel
```

### Deploy lên Netlify
1. Build project: `npm run build`
2. Upload thư mục `dist/` lên Netlify

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Liên hệ

- Email: your-email@example.com
- Project Link: [https://github.com/yourusername/language-learning-platform](https://github.com/yourusername/language-learning-platform)