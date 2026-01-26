# Dự án: Học Từ Vựng (Django REST API)

## Giới thiệu
API backend phục vụ ứng dụng học từ vựng. Hỗ trợ đăng ký người dùng, đăng nhập bằng Google thông qua id_token và cấp phát JWT (SimpleJWT) để truy cập các API bảo vệ.

## Công nghệ sử dụng
- Django 4.2
- Django REST Framework (DRF)
- SimpleJWT (JWT Access/Refresh)
- CORS Headers
- dj-rest-auth, django-allauth (cấu hình sẵn; login Google dùng id_token custom endpoint)
- MySQL (mysql-connector-python)
- requests (xác thực id_token với Google)

## Cấu trúc chính
- `core/settings.py`: cấu hình project, DB, JWT, CORS, allauth
- `core/urls.py`: định tuyến các endpoint chính
- `vocabulary/`: app quản lý người dùng và khóa học ví dụ
  - `views.py`: các view API, bao gồm `GoogleIdTokenLoginView`
  - `urls.py`: route của app

## Yêu cầu hệ thống
- Python 3.8+ (khuyến nghị 3.10/3.11 nếu phù hợp môi trường)
- MySQL Server 5.7+/8.0+
- pip, virtualenv

## Cài đặt và chạy (Windows)
1) Clone dự án và tạo môi trường ảo
```bash
cd D:\DOAn
python -m venv venv
venv\Scripts\activate
```

2) Cài phụ thuộc
```bash
pip install -U pip
pip install django==4.2.* djangorestframework django-cors-headers djangorestframework-simplejwt dj-rest-auth django-allauth mysql-connector-python requests
```

3) Cấu hình database MySQL
- Tạo database (ví dụ): `django_vocab`
- Cập nhật thông tin trong `core/settings.py` phần `DATABASES` cho `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` theo hệ thống của bạn.

4) Cấu hình Google OAuth (id_token)
- Lấy `Client ID` và `Client Secret` từ Google Cloud Console (OAuth 2.0 Client IDs)
- Cập nhật vào `SOCIALACCOUNT_PROVIDERS['google']['APP']` trong `core/settings.py`
  - `client_id` phải khớp với phía front-end để check `aud`

5) Tạo bảng và chạy server
```bash
python manage.py migrate
python manage.py runserver
```
Server chạy tại `http://127.0.0.1:8000/`.

## API chính
- Đăng ký người dùng: `POST /api/register/`
- Lấy token chuẩn (username/password):
  - `POST /api/token/`
  - `POST /api/token/refresh/`
- Đăng nhập Google bằng id_token: `POST /api/auth/google/id-token/`
  - Body JSON: `{ "id_token": "<GOOGLE_ID_TOKEN>" }`
  - Trả về: `{ "access": "...", "refresh": "..." }`
- Khóa học (yêu cầu `Authorization: Bearer <access>`):
  - `GET /api/courses/`
  - `GET /api/courses/<id>/`

## Cách hoạt động đăng nhập Google (id_token)
- Frontend dùng Google Identity Services nhận `credential` (id_token) từ Google
- Gửi `id_token` tới `POST /api/auth/google/id-token/`
- Backend xác thực với Google (`https://oauth2.googleapis.com/tokeninfo`), kiểm tra `aud`, `iss`, `exp`
- Tìm hoặc tạo người dùng theo email, trả về JWT `access`/`refresh`

Ví dụ gọi từ frontend (pseudo):
```js
const res = await fetch('http://localhost:8000/api/auth/google/id-token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id_token }),
});
const data = await res.json();
localStorage.setItem('access_token', data.access);
```

## Ghi chú bảo mật
- Không nên commit `SECRET_KEY`, `Client Secret` hoặc thông tin DB thật. Hãy chuyển sang dùng biến môi trường trong triển khai thực tế.
- Cấu hình `ALLOWED_HOSTS` phù hợp khi đưa lên production.

## Kiểm thử nhanh
```bash
# Kiểm tra cấu hình
python manage.py check

# Gọi API (ví dụ cần access token hợp lệ)
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/courses/
```

## License
MIT (hoặc tùy chọn của bạn) 