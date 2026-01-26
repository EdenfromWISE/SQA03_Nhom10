# Quick Start Guide - Learning App

Hướng dẫn nhanh cho người tiếp nhận dự án.

## 📚 Tài Liệu Quan Trọng

1. **[README.md](../README.md)** - Tổng quan về app
2. **[QUESTION_TYPES_GUIDE.md](QUESTION_TYPES_GUIDE.md)** - Hướng dẫn thêm/bớt question types
3. **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Tóm tắt các thay đổi

## 🚀 Cách Thêm Question Type Mới (3 Bước)

### Bước 1: Tạo File Mới

Tạo file `learning/services/question_types/my_new_type.py`:

```python
from typing import Any, Dict, Optional, List
from vocabulary.models import Vocabulary
from .base import QuestionTypeBase

class MyNewQuestionType(QuestionTypeBase):
    QUESTION_TYPE = "my_new_type"
    DISPLAY_NAME = "Tên Hiển Thị"
    
    @classmethod
    def build_question(cls, vocabulary, pool=None, **kwargs):
        return {
            "id": f"mytype_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Tiêu đề câu hỏi",
            "prompt": {"definition": vocabulary.meaning},
            "answer": vocabulary.word,
            "metadata": {"vocabulary_id": vocabulary.id},
        }
    
    @classmethod
    def evaluate_answer(cls, user_answer, question, pronunciation_score=None):
        is_correct = user_answer == question["answer"]
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Đúng!" if is_correct else "Sai!",
        }
    
    @classmethod
    def requires_pool(cls):
        return False  # True nếu cần pool để tạo phương án nhiễu
```

### Bước 2: Đăng Ký

Mở `learning/services/question_types/__init__.py` và thêm:

```python
from .my_new_type import MyNewQuestionType
registry.register(MyNewQuestionType)
```

### Bước 3: Xong!

Question type mới đã sẵn sàng sử dụng! 🎉

## ❌ Cách Loại Bỏ Question Type

### Cách 1: Comment Dòng Đăng Ký (Khuyến Nghị)

Trong `learning/services/question_types/__init__.py`:

```python
# registry.register(SpeakingQuestionType)  # Đã bị comment
```

### Cách 2: Xóa Hoàn Toàn

1. Xóa file question type
2. Xóa import và đăng ký trong `__init__.py`

## 🔧 Kiểm Tra Question Types

```python
from learning.services.question_types.registry import registry

# Xem tất cả question types
print(registry.get_all_types())

# Kiểm tra một question type
if registry.is_registered("listening"):
    print("Listening đã được đăng ký!")
```

## 📖 Xem Chi Tiết

- **Thêm question type phức tạp?** → Xem [QUESTION_TYPES_GUIDE.md](QUESTION_TYPES_GUIDE.md)
- **Cần hiểu kiến trúc?** → Xem [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- **Tổng quan app?** → Xem [README.md](../README.md)

## 🆘 Gặp Vấn Đề?

1. Kiểm tra question type đã được đăng ký chưa
2. Kiểm tra `QUESTION_TYPE` có unique không
3. Kiểm tra import có lỗi không
4. Xem phần Troubleshooting trong [QUESTION_TYPES_GUIDE.md](QUESTION_TYPES_GUIDE.md)

