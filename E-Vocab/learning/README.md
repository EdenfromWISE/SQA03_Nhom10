# Learning App

App quản lý hệ thống học tập từ vựng tiếng Anh với nhiều loại câu hỏi khác nhau.

## Tổng Quan

Learning app cung cấp các tính năng:

- ✅ **Practice Session**: Luyện tập từ vựng theo topic
- ✅ **Review Session**: Ôn tập từ vựng theo SRS (Spaced Repetition System)
- ✅ **Exam Session**: Kiểm tra kiến thức với thời gian giới hạn
- ✅ **Multiple Question Types**: Nhiều loại câu hỏi (listening, reading, writing, matching, speaking)
- ✅ **Progress Tracking**: Theo dõi tiến độ học tập
- ✅ **Pronunciation Assessment**: Đánh giá phát âm bằng AI

## Cấu Trúc

```
learning/
├── models.py              # Models: LearningSession, Question, UserAnswer, LearningConfig
├── views.py               # API endpoints
├── serializers.py         # DRF serializers
├── urls.py                # URL routing
├── admin.py               # Django admin configuration
├── services/
│   ├── question_service.py          # Service tạo/đánh giá câu hỏi
│   ├── sessions_service.py          # Service quản lý sessions
│   ├── pronunciation_ai.py          # AI đánh giá phát âm
│   └── question_types/              # Các loại câu hỏi
│       ├── base.py                  # Base class cho question types
│       ├── registry.py              # Registry pattern
│       ├── listening.py
│       ├── reading.py
│       ├── writing.py
│       ├── matching.py
│       └── speaking.py
└── docs/
    └── QUESTION_TYPES_GUIDE.md      # Hướng dẫn bổ sung/loại bỏ question types
```

## Kiến Trúc

### Design Patterns

1. **Strategy Pattern**: Mỗi question type là một strategy riêng biệt
2. **Registry Pattern**: Quản lý các question types động
3. **Service Layer**: Business logic được tách riêng khỏi views

### SOLID Principles

- ✅ **Single Responsibility**: Mỗi class có một trách nhiệm duy nhất
- ✅ **Open/Closed**: Dễ dàng mở rộng (thêm question types) mà không sửa code hiện có
- ✅ **Liskov Substitution**: Tất cả question types có thể thay thế lẫn nhau
- ✅ **Interface Segregation**: Base class chỉ định nghĩa những gì cần thiết
- ✅ **Dependency Inversion**: Phụ thuộc vào abstraction (registry) thay vì concrete classes

## API Endpoints

### Sessions

- `POST /learning/sessions/practice/` - Tạo practice session
- `POST /learning/sessions/review/` - Tạo review session
- `POST /learning/sessions/exam/` - Tạo exam session
- `GET /learning/sessions/<id>/` - Lấy thông tin session
- `GET /learning/sessions/<id>/detail/` - Lấy chi tiết session
- `GET /learning/sessions/<id>/questions/` - Lấy danh sách câu hỏi
- `POST /learning/sessions/<id>/submit-answer/` - Gửi câu trả lời
- `POST /learning/sessions/<id>/complete/` - Hoàn thành session
- `POST /learning/sessions/<id>/cancel/` - Hủy session
- `GET /learning/sessions/history/` - Lấy lịch sử sessions

### Pronunciation

- `POST /learning/pronunciation/assess/` - Đánh giá phát âm

## Question Types

### Hiện Tại

1. **listening** - Nghe và chọn nghĩa đúng của từ
2. **reading** - Đọc nghĩa và chọn từ tiếng Anh
3. **writing** - Đọc nghĩa và nhập từ tiếng Anh
4. **matching** - Ghép cặp từ với nghĩa
5. **speaking** - Phát âm từ tiếng Anh

### Thêm/Bớt Question Types

Xem [QUESTION_TYPES_GUIDE.md](docs/QUESTION_TYPES_GUIDE.md) để biết chi tiết.

## Models

### LearningSession

Lưu trữ thông tin về một phiên học tập:
- `user`: Người dùng
- `topic`: Topic học tập (có thể null cho review session)
- `mode`: Chế độ (practice, review, exam)
- `time_limit`: Thời gian giới hạn (phút)
- `total_questions`: Tổng số câu hỏi
- `pass_score`: Điểm đạt (%)
- `score`: Điểm số đạt được
- `is_passed`: Đã đạt hay chưa

### Question

Lưu trữ thông tin về một câu hỏi:
- `session`: Phiên học tập
- `vocabulary`: Từ vựng liên quan
- `question_type`: Loại câu hỏi
- `order`: Thứ tự câu hỏi
- `content`: Nội dung câu hỏi (JSON)
- `correct_answer`: Đáp án đúng (JSON)
- `explanation`: Giải thích

### UserAnswer

Lưu trữ câu trả lời của người dùng:
- `session`: Phiên học tập
- `question`: Câu hỏi
- `selected_option`: Phương án đã chọn
- `answer_text`: Văn bản trả lời
- `is_correct`: Đúng hay sai
- `time_spent`: Thời gian làm (giây)

### LearningConfig

Cấu hình chung (Singleton):
- `time_limit`: Thời gian giới hạn mặc định
- `total_questions`: Số câu hỏi mặc định
- `pass_score`: Điểm đạt mặc định
- `max_daily_exams_per_topic`: Số lần thi tối đa mỗi ngày

## Services

### QuestionService

Service tạo và đánh giá câu hỏi:
- `generate_session_questions()`: Tạo danh sách câu hỏi cho session
- `evaluate_answer()`: Đánh giá câu trả lời
- `get_available_question_types()`: Lấy danh sách question types có sẵn

### SessionsService

Service quản lý sessions:
- `create_practice_session()`: Tạo practice session
- `create_review_session()`: Tạo review session
- `create_exam_session()`: Tạo exam session
- `submit_answer()`: Xử lý câu trả lời
- `complete_session()`: Hoàn thành session
- `cancel_session()`: Hủy session

## Dependencies

- Django 4.2+
- Django REST Framework
- django-solo (cho SingletonModel)
- torch, transformers (cho pronunciation AI)
- librosa, g2p_en (cho pronunciation assessment)

## Testing

```bash
# Chạy tests
python manage.py test learning

# Test question types
python manage.py test learning.tests.question_types
```

## Migration

```bash
# Tạo migrations
python manage.py makemigrations learning

# Apply migrations
python manage.py migrate learning
```

## Tài Liệu Tham Khảo

- [QUESTION_TYPES_GUIDE.md](docs/QUESTION_TYPES_GUIDE.md) - Hướng dẫn bổ sung/loại bỏ question types

## Liên Hệ

Nếu có câu hỏi hoặc vấn đề, vui lòng liên hệ team phát triển.

