# Selenium Test — E-Vocab (Selenium WebDriver + pytest)

Auto kiểm thử 24 test case theo checklist `test.md.txt`:

| Module | Test cases |
|---|---|
| REG-ST | 02, 04, 06, 09, 16 |
| LOG-ST | 01, 02 (empty + format), 16 |
| UM-ST | 01, 02, 03, 04 |
| ADMIN-SRCH | HP-01, HP-02, HP-03, NG-02, UI-01 |
| USER-SRCH | NG-01, BD-01, UI-01 |
| FLC-ST | 03-H, 07-L |
| PG-ST | 01-H, 01-T2 |
| SEC-ST / CMN-ST | 01-L, 01-L (3 routes) |

## 1. Chuẩn bị môi trường

```bash
cd "C:/Users/WS-EDEN/Coding Stuff/SQA/SQA03_Nhom10"
python -m venv venv-sys
venv-sys\Scripts\activate
pip install -r selenium_test/requirements.txt
```

Cần Chrome đã cài sẵn (Selenium dùng `webdriver-manager` tự tải đúng phiên bản driver).

## 2. Cấu hình

```bash
cd selenium_test
cp .env.example .env   # Windows:  copy .env.example .env
# Sửa DB_PASSWORD, ADMIN_*, TEST_USER_* nếu khác
```

## 3. Khởi động backend + frontend

Mở 2 terminal song song:

```bash
# Terminal 1
cd E-Vocab
python manage.py runserver
```

```bash
# Terminal 2
cd FE-E-Vocab
npm install   # lần đầu
npm run dev
```

## 4. Seed dữ liệu test (1 lần)

```bash
cd selenium_test
python seed_data.py
```

Script sẽ tạo:
- Superuser `admin/admin123` (cho UM-ST-01/03/04)
- User test `sysauto_user@test.local / Abc@12345` (đã active + email verified)

Nếu seed bằng ORM thất bại (thường do thiếu env), hãy chạy thủ công:

```bash
cd E-Vocab
python manage.py createsuperuser    # username=admin, password=admin123
```

Đảm bảo trong DB có ít nhất một số từ chứa `apple` (cho ADMIN-SRCH) và một topic
có vocabulary để test flashcard (`TEST_TOPIC_ID` trong `.env`).

## 5. Chạy test

```bash
cd selenium_test
pytest                          # chạy tất cả + xuất report HTML
pytest tests/test_log_st.py     # chạy 1 module
pytest -k "REG-ST-04"           # chạy 1 case theo id
pytest -m fe                    # chỉ test frontend
pytest -m admin                 # chỉ test admin
HEADLESS=1 pytest               # chạy ẩn browser (Linux/Mac)
set HEADLESS=1 && pytest        # chạy ẩn browser (Windows cmd)
```

## 6. Báo cáo

Sau khi chạy, mở `reports/report.html` (HTML self-contained, kèm ảnh chụp khi
fail trong `reports/screenshots/`).

## 7. Rollback

- Dữ liệu user test luôn dùng prefix `sysauto_*` -> fixture autouse cuối session
  sẽ `DELETE FROM auth_user WHERE email LIKE 'sysauto_%'`.
- Test UM-ST-04 set `is_active=False` rồi tự khôi phục `True` ở finally.
- Test PG-ST-01-T2 xoá progress của user test (giả lập user mới); progress sẽ
  được tự build lại khi user dùng app.

## 8. Cấu trúc

```
selenium_test/
├── conftest.py          # driver, fixture, hook chụp ảnh, cleanup DB
├── pytest.ini
├── .env.example
├── seed_data.py
├── requirements.txt
├── data/                # CSV/Excel data-driven
├── pages/               # Page Object Model
├── tests/               # 8 file test phủ 24 case
├── utils/               # db_helper, excel_reader
└── reports/             # report.html + screenshots/
```

## 9. Cách thêm test case mới

1. Thêm dòng dữ liệu vào file CSV trong `data/`.
2. Nếu gặp trang mới: tạo Page Object trong `pages/`.
3. Viết hàm test trong `tests/test_*.py`, dùng `@pytest.mark.parametrize`
   từ `excel_reader.load_csv` để loop qua dữ liệu.
4. Verify cả UI lẫn DB (qua `utils.db_helper.fetch_one/...`).
5. Chạy `pytest -k <tc_id>`.
