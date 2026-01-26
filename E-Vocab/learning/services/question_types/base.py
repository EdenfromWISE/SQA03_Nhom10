"""
Base class và interface cho các loại câu hỏi.

Mỗi question type phải implement 2 phương thức chính:
- build_question: Tạo câu hỏi từ vocabulary
- evaluate_answer: Đánh giá câu trả lời của người dùng
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary


class QuestionTypeBase(ABC):
    """
    Base class cho tất cả các loại câu hỏi.
    
    Tuân theo Strategy pattern và Open/Closed principle:
    - Dễ dàng thêm/bớt question types mà không cần sửa code hiện có
    - Mỗi question type tự quản lý logic của mình
    """
    
    # Phải được định nghĩa trong subclass
    QUESTION_TYPE: str = ""
    DISPLAY_NAME: str = ""
    
    @classmethod
    @abstractmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo một câu hỏi từ vocabulary.
        
        Args:
            vocabulary: Từ vựng chính để tạo câu hỏi
            pool: Danh sách từ vựng để tạo phương án nhiễu (nếu cần)
            **kwargs: Các tham số bổ sung tùy theo loại câu hỏi
            
        Returns:
            Dict chứa:
                - id: ID duy nhất của câu hỏi
                - type: Loại câu hỏi (phải trùng với QUESTION_TYPE)
                - title: Tiêu đề câu hỏi
                - prompt: Nội dung câu hỏi (JSON)
                - answer: Đáp án đúng
                - explanation: Giải thích (tùy chọn)
                - metadata: Thông tin bổ sung (tùy chọn)
        """
        pass
    
    @classmethod
    @abstractmethod
    def evaluate_answer(
        cls,
        user_answer: Any,
        question: Dict[str, Any],
        pronunciation_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Đánh giá câu trả lời của người dùng.
        
        Args:
            user_answer: Câu trả lời của người dùng (có thể là int, str, dict, file, etc.)
            question: Câu hỏi đã được tạo (chứa đáp án đúng)
            pronunciation_score: Điểm phát âm (chỉ dùng cho speaking questions)
            
        Returns:
            Dict chứa:
                - is_correct: Boolean
                - score: Float (0.0 - 1.0)
                - feedback: String
        """
        pass
    
    @classmethod
    def requires_pool(cls) -> bool:
        """
        Kiểm tra xem loại câu hỏi này có cần pool vocabulary để tạo phương án nhiễu không.
        
        Returns:
            True nếu cần pool, False nếu chỉ cần vocabulary chính
        """
        return True
    
    @classmethod
    def validate_question_data(cls, question_data: Dict[str, Any]) -> bool:
        """
        Validate dữ liệu câu hỏi trước khi lưu.
        
        Args:
            question_data: Dict chứa dữ liệu câu hỏi
            
        Returns:
            True nếu hợp lệ, False nếu không
        """
        required_fields = ["id", "type", "title", "prompt", "answer"]
        return all(field in question_data for field in required_fields)

