# Hướng Dẫn Bổ Sung và Loại Bỏ Question Types

Tài liệu này hướng dẫn cách bổ sung hoặc loại bỏ các loại câu hỏi (question types) trong hệ thống học tập E-Vocab.

## Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
3. [Bổ Sung Question Type Mới](#bổ-sung-question-type-mới)
4. [Loại Bỏ Question Type](#loại-bỏ-question-type)
5. [Tạm Thời Vô Hiệu Hóa Question Type](#tạm-thời-vô-hiệu-hóa-question-type)
6. [Cấu Hình Question Types](#cấu-hình-question-types)
7. [Ví Dụ Thực Tế](#ví-dụ-thực-tế)
8. [Kiểm Tra và Testing](#kiểm-tra-và-testing)

---

## Tổng Quan

Hệ thống sử dụng **Registry Pattern** và **Strategy Pattern** để quản lý các loại câu hỏi. Điều này cho phép:

- ✅ Dễ dàng thêm/bớt question types mà không cần sửa code core
- ✅ Tuân theo nguyên tắc SOLID (đặc biệt là Open/Closed Principle)
- ✅ Mỗi question type tự quản lý logic riêng của mình
- ✅ Dễ dàng test và maintain

### Các Question Types Hiện Tại

1. **listening** - Nghe và chọn nghĩa đúng của từ
2. **reading** - Đọc nghĩa và chọn từ tiếng Anh
3. **writing** - Đọc nghĩa và nhập từ tiếng Anh
4. **matching** - Ghép cặp từ với nghĩa
5. **speaking** - Phát âm từ tiếng Anh (có thể bị vô hiệu hóa)

---

## Kiến Trúc Hệ Thống

### Cấu Trúc Thư Mục

```
learning/
├── services/
│   ├── question_service.py          # Service chính để tạo/đánh giá câu hỏi
│   └── question_types/
│       ├── __init__.py              # Đăng ký các question types
│       ├── base.py                  # Base class cho tất cả question types
│       ├── registry.py              # Registry pattern để quản lý
│       ├── listening.py             # Question type: listening
│       ├── reading.py               # Question type: reading
│       ├── writing.py               # Question type: writing
│       ├── matching.py              # Question type: matching
│       └── speaking.py              # Question type: speaking
```

### Base Class

Tất cả question types phải kế thừa từ `QuestionTypeBase` trong `base.py`:

```python
class QuestionTypeBase(ABC):
    QUESTION_TYPE: str = ""          # Phải được định nghĩa
    DISPLAY_NAME: str = ""           # Tên hiển thị
    
    @classmethod
    @abstractmethod
    def build_question(...) -> Dict[str, Any]:
        """Tạo câu hỏi từ vocabulary"""
        pass
    
    @classmethod
    @abstractmethod
    def evaluate_answer(...) -> Dict[str, Any]:
        """Đánh giá câu trả lời của người dùng"""
        pass
```

### Registry Pattern

Registry tự động quản lý các question types. Khi import module `question_types`, tất cả các question types sẽ được đăng ký tự động.

---

## Bổ Sung Question Type Mới

### Bước 1: Tạo File Question Type Mới

Tạo file mới trong `learning/services/question_types/`, ví dụ: `multiple_choice.py`

```python
"""
Question type: Multiple Choice - Câu hỏi trắc nghiệm nhiều lựa chọn.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary
from .base import QuestionTypeBase


class MultipleChoiceQuestionType(QuestionTypeBase):
    """Câu hỏi trắc nghiệm nhiều lựa chọn."""
    
    QUESTION_TYPE = "multiple_choice"  # Phải là unique identifier
    DISPLAY_NAME = "Câu hỏi trắc nghiệm"  # Tên hiển thị cho người dùng
    
    @classmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        options: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo câu hỏi multiple choice.
        
        Args:
            vocabulary: Từ vựng chính
            pool: Danh sách từ vựng để tạo phương án nhiễu
            options: Số lượng phương án (mặc định 4)
        
        Returns:
            Dict chứa thông tin câu hỏi với format:
            {
                "id": str,              # ID duy nhất
                "type": str,            # Loại câu hỏi
                "title": str,           # Tiêu đề
                "prompt": dict,         # Nội dung câu hỏi
                "answer": Any,          # Đáp án đúng
                "explanation": str,     # Giải thích (tùy chọn)
                "metadata": dict,       # Metadata (tùy chọn)
            }
        """
        if pool is None:
            pool = []
        
        # Tạo phương án nhiễu
        distractors = cls._pick_distractors(vocabulary, pool, options - 1)
        choices = [vocabulary.word, *distractors]
        random.shuffle(choices)
        
        question_data = {
            "id": f"mc_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Chọn từ đúng với nghĩa",
            "prompt": {
                "definition": vocabulary.meaning,
                "options": choices,
            },
            "answer": choices.index(vocabulary.word),
            "explanation": f"'{vocabulary.meaning}' có nghĩa là '{vocabulary.word}'",
            "metadata": {"vocabulary_id": vocabulary.id},
        }
        
        # Validate dữ liệu
        if not cls.validate_question_data(question_data):
            raise ValueError(f"Dữ liệu câu hỏi không hợp lệ: {question_data}")
        
        return question_data
    
    @classmethod
    def evaluate_answer(
        cls,
        user_answer: Any,
        question: Dict[str, Any],
        pronunciation_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Đánh giá câu trả lời.
        
        Args:
            user_answer: Câu trả lời của người dùng (có thể là int, str, dict, etc.)
            question: Câu hỏi đã được tạo
            pronunciation_score: Điểm phát âm (nếu có, thường không dùng)
        
        Returns:
            Dict với format:
            {
                "is_correct": bool,     # Đúng/Sai
                "score": float,         # Điểm số (0.0 - 1.0)
                "feedback": str,        # Phản hồi cho người dùng
            }
        """
        correct_answer = question.get("answer")
        is_correct = isinstance(user_answer, int) and user_answer == correct_answer
        
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Chính xác!" if is_correct else "Chưa đúng, hãy thử lại.",
        }
    
    @classmethod
    def requires_pool(cls) -> bool:
        """
        Xác định xem question type này có cần pool vocabulary để tạo phương án nhiễu không.
        
        Returns:
            True nếu cần pool, False nếu chỉ cần vocabulary chính
        """
        return True
    
    @classmethod
    def _pick_distractors(
        cls, target: Vocabulary, pool: List[Vocabulary], count: int
    ) -> List[str]:
        """Helper method để tạo phương án nhiễu."""
        candidates = [v for v in pool if v.id != target.id]
        selected = random.sample(candidates, min(count, len(candidates)))
        return [v.word for v in selected]
```

### Bước 2: Đăng Ký Question Type

Mở file `learning/services/question_types/__init__.py` và thêm:

```python
# Import question type mới
from .multiple_choice import MultipleChoiceQuestionType

# Đăng ký question type
registry.register(MultipleChoiceQuestionType)
```

### Bước 3: Kiểm Tra

Sau khi đăng ký, question type mới sẽ tự động có sẵn trong hệ thống. Bạn có thể kiểm tra bằng cách:

```python
from learning.services.question_types.registry import registry

# Kiểm tra xem đã đăng ký chưa
print(registry.get_all_types())  # Sẽ bao gồm "multiple_choice"

# Lấy class của question type
question_type_class = registry.get("multiple_choice")
```

### Bước 4: Test Question Type

Tạo test để đảm bảo question type hoạt động đúng:

```python
from learning.services.question_types import MultipleChoiceQuestionType
from vocabulary.models import Vocabulary

# Test build_question
vocabulary = Vocabulary.objects.first()
question = MultipleChoiceQuestionType.build_question(vocabulary, pool=[])

# Test evaluate_answer
result = MultipleChoiceQuestionType.evaluate_answer(
    user_answer=0,  # Index của phương án
    question=question
)
```

---

## Loại Bỏ Question Type

### Cách 1: Xóa Khỏi Registry (Khuyến Nghị)

Chỉ cần comment hoặc xóa dòng đăng ký trong `__init__.py`:

```python
# learning/services/question_types/__init__.py

# Bỏ đăng ký listening question type
# registry.register(ListeningQuestionType)  # Đã bị comment

# Hoặc xóa hoàn toàn
# from .listening import ListeningQuestionType  # Xóa dòng import
# registry.register(ListeningQuestionType)      # Xóa dòng đăng ký
```

**Lưu ý:** File `listening.py` vẫn tồn tại nhưng sẽ không được sử dụng trong hệ thống.

### Cách 2: Sử Dụng Unregister Method

Có thể unregister trong runtime:

```python
from learning.services.question_types.registry import registry

# Unregister question type
registry.unregister("listening")
```

### Cách 3: Xóa Hoàn Toàn File

Nếu chắc chắn không cần dùng nữa:

1. Xóa file `learning/services/question_types/listening.py`
2. Xóa import và đăng ký trong `__init__.py`
3. Xóa các test liên quan (nếu có)

**⚠️ Cảnh Báo:** Hãy đảm bảo không có code nào khác đang sử dụng question type này trước khi xóa.

---

## Tạm Thời Vô Hiệu Hóa Question Type

Để tạm thời vô hiệu hóa một question type (ví dụ: speaking khi chưa sẵn sàng):

### Cách 1: Comment Dòng Đăng Ký

```python
# learning/services/question_types/__init__.py

# Speaking có thể bị comment nếu chưa sẵn sàng
# registry.register(SpeakingQuestionType)  # Bị comment
```

### Cách 2: Sử Dụng Enabled Types

Khi tạo session, chỉ định các question types được bật:

```python
from learning.services.sessions_service import SessionsService

service = SessionsService()
session = service.create_practice_session(
    user=user,
    topic=topic,
    enabled_types=["listening", "reading", "writing"]  # Không bao gồm speaking
)
```

---

## Cấu Hình Question Types

### Lấy Danh Sách Question Types Có Sẵn

```python
from learning.services.question_types.registry import registry

# Lấy tất cả các loại
types = registry.get_all_types()
# Output: ['listening', 'reading', 'writing', 'matching', 'speaking']

# Lấy display names
display_names = registry.get_display_names()
# Output: {
#     'listening': 'Nghe và chọn nghĩa',
#     'reading': 'Đọc nghĩa và chọn từ',
#     ...
# }
```

### Phân Bố Câu Hỏi Tùy Chỉnh

Khi tạo session, có thể chỉ định phân bố câu hỏi:

```python
service = SessionsService()
session = service.create_practice_session(
    user=user,
    topic=topic,
    question_distribution={
        "listening": 5,   # 5 câu listening
        "reading": 5,     # 5 câu reading
        "writing": 3,     # 3 câu writing
        "matching": 2,    # 2 câu matching
    },
    total_questions=15,   # Tổng 15 câu
)
```

---

## Ví Dụ Thực Tế

### Ví Dụ 1: Thêm Question Type "True/False"

**File:** `learning/services/question_types/true_false.py`

```python
from typing import Any, Dict, Optional, List
from vocabulary.models import Vocabulary
from .base import QuestionTypeBase

class TrueFalseQuestionType(QuestionTypeBase):
    QUESTION_TYPE = "true_false"
    DISPLAY_NAME = "Đúng/Sai"
    
    @classmethod
    def build_question(cls, vocabulary: Vocabulary, pool: Optional[List[Vocabulary]] = None, **kwargs) -> Dict[str, Any]:
        # Tạo một statement đúng hoặc sai
        import random
        is_true = random.choice([True, False])
        
        return {
            "id": f"tf_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Câu này đúng hay sai?",
            "prompt": {
                "statement": f"'{vocabulary.word}' có nghĩa là '{vocabulary.meaning}'",
            },
            "answer": is_true,
            "explanation": f"Đây là {'đúng' if is_true else 'sai'}",
            "metadata": {"vocabulary_id": vocabulary.id},
        }
    
    @classmethod
    def evaluate_answer(cls, user_answer: Any, question: Dict[str, Any], pronunciation_score: Optional[float] = None) -> Dict[str, Any]:
        is_correct = user_answer == question["answer"]
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Đúng!" if is_correct else "Sai!",
        }
    
    @classmethod
    def requires_pool(cls) -> bool:
        return False
```

**Đăng ký trong `__init__.py`:**

```python
from .true_false import TrueFalseQuestionType
registry.register(TrueFalseQuestionType)
```

### Ví Dụ 2: Loại Bỏ Question Type "Speaking"

**File:** `learning/services/question_types/__init__.py`

```python
# Comment dòng đăng ký
# registry.register(SpeakingQuestionType)
```

Hoặc xóa hoàn toàn:

```python
# Xóa import
# from .speaking import SpeakingQuestionType

# Xóa đăng ký
# registry.register(SpeakingQuestionType)
```

---

## Kiểm Tra và Testing

### 1. Kiểm Tra Registry

```python
from learning.services.question_types.registry import registry

# Kiểm tra question type có tồn tại không
assert registry.is_registered("listening")

# Lấy class
cls = registry.get("listening")
assert cls is not None
```

### 2. Test Build Question

```python
from learning.services.question_types import ListeningQuestionType
from vocabulary.models import Vocabulary

vocabulary = Vocabulary.objects.first()
vocabularies = list(Vocabulary.objects.all()[:10])

question = ListeningQuestionType.build_question(
    vocabulary=vocabulary,
    pool=vocabularies
)

assert question["type"] == "listening"
assert "prompt" in question
assert "answer" in question
```

### 3. Test Evaluate Answer

```python
result = ListeningQuestionType.evaluate_answer(
    user_answer=0,
    question=question
)

assert "is_correct" in result
assert "score" in result
assert "feedback" in result
```

### 4. Test Tích Hợp

```python
from learning.services.question_service import QuestionService

service = QuestionService()

# Test generate questions với question type mới
questions = service.generate_session_questions(
    vocabularies=vocabularies,
    total_questions=10,
    enabled_types=["listening", "reading"]  # Chỉ dùng 2 loại
)

assert len(questions) == 10
assert all(q["type"] in ["listening", "reading"] for q in questions)
```

---

## Lưu Ý Quan Trọng

1. **QUESTION_TYPE phải unique:** Mỗi question type phải có identifier duy nhất
2. **Validate dữ liệu:** Luôn validate dữ liệu câu hỏi trước khi trả về
3. **Error handling:** Xử lý lỗi một cách rõ ràng và cung cấp feedback hữu ích
4. **Tương thích ngược:** Giữ lại các hàm cũ (deprecated) nếu cần tương thích
5. **Documentation:** Viết docstring rõ ràng cho mỗi method
6. **Testing:** Luôn test kỹ trước khi deploy

---

## Troubleshooting

### Question Type Không Xuất Hiện

- Kiểm tra xem đã đăng ký trong `__init__.py` chưa
- Kiểm tra xem QUESTION_TYPE có đúng format không
- Kiểm tra import có lỗi không

### Lỗi "Loại câu hỏi không hợp lệ"

- Kiểm tra registry có question type đó không: `registry.is_registered("type_name")`
- Kiểm tra spelling của question type

### Câu Hỏi Không Được Tạo

- Kiểm tra xem vocabulary có đủ không
- Kiểm tra enabled_types có bao gồm question type đó không
- Kiểm tra logic trong build_question

---

## Tài Liệu Tham Khảo

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Registry Pattern](https://martinfowler.com/eaaCatalog/registry.html)

---

## Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra lại tài liệu này
2. Xem các ví dụ trong code hiện tại
3. Liên hệ team phát triển

---

**Tài liệu được cập nhật lần cuối:** 2024

