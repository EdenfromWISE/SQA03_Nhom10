"""
Service để tạo và đánh giá các loại câu hỏi từ vựng khác nhau.

Sử dụng registry pattern để quản lý question types, cho phép dễ dàng
thêm/bớt question types mà không cần sửa code core.
"""
import random
from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary
# Import để đảm bảo các question types được đăng ký tự động
from learning.services import question_types  # noqa: F401
from learning.services.question_types.registry import registry


class QuestionService:
    """
    Service để tạo các loại câu hỏi từ vựng khác nhau.
    
    Tuân theo Dependency Inversion principle:
    - Phụ thuộc vào abstraction (registry) thay vì concrete implementations
    - Dễ dàng mở rộng mà không cần sửa code hiện có (Open/Closed principle)
    """

    def __init__(self):
        """Khởi tạo QuestionService với registry."""
        self.registry = registry

    def get_available_question_types(self) -> Dict[str, str]:
        """
        Lấy danh sách các loại câu hỏi có sẵn.
        
        Returns:
            Dict mapping question_type -> display_name
        """
        return self.registry.get_display_names()

    def generate_session_questions(
        self,
        vocabularies: List[Vocabulary],
        total_questions: Optional[int] = None,
        question_distribution: Optional[Dict[str, int]] = None,
        enabled_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Tạo câu hỏi cho bài kiểm tra theo cấu trúc cố định.

        Args:
            vocabularies: Danh sách từ vựng để tạo câu hỏi
            total_questions: Tổng số câu hỏi (tùy chọn)
            question_distribution: Phân bố số câu hỏi theo loại (tùy chọn)
            enabled_types: Danh sách các loại câu hỏi được bật (tùy chọn)
                          Nếu None, sử dụng tất cả các loại đã đăng ký

        Returns:
            List[Dict]: Danh sách câu hỏi được tạo
        """
        if not vocabularies:
            raise ValueError("Danh sách từ vựng không thể rỗng")

        # Lọc các question types được bật
        available_types = self.registry.get_all_types()
        if enabled_types is not None:
            # Kiểm tra tất cả các enabled_types đều tồn tại
            invalid_types = set(enabled_types) - set(available_types)
            if invalid_types:
                raise ValueError(
                    f"Các loại câu hỏi không hợp lệ: {', '.join(invalid_types)}"
                )
            available_types = [t for t in available_types if t in enabled_types]
        
        if not available_types:
            raise ValueError("Không có loại câu hỏi nào được kích hoạt")

        # Xác định tập từ vựng cuối cùng
        if total_questions and total_questions < len(vocabularies):
            shuffled_vocabularies = random.sample(vocabularies, total_questions)
        else:
            shuffled_vocabularies = list(vocabularies)

        # Tính toán phân bố câu hỏi
        if question_distribution:
            questions_per_type = question_distribution
        else:
            questions_per_type = self._calculate_question_distribution(
                shuffled_vocabularies, available_types
            )

        # Tạo câu hỏi
        all_questions = []
        vocab_index = 0

        for question_type in available_types:
            count = questions_per_type.get(question_type, 0)
            for i in range(count):
                if vocab_index >= len(shuffled_vocabularies):
                    break

                vocabulary = shuffled_vocabularies[vocab_index]
                question = self._create_question(
                    vocabulary, question_type, vocabularies
                )
                all_questions.append(question)
                vocab_index += 1

        # Trộn thứ tự câu hỏi
        random.shuffle(all_questions)
        return all_questions

    def _calculate_question_distribution(
        self, vocabularies: List[Vocabulary], available_types: List[str]
    ) -> Dict[str, int]:
        """
        Tính toán phân bố câu hỏi dựa trên số lượng từ vựng.

        Args:
            vocabularies: Danh sách từ vựng
            available_types: Danh sách các loại câu hỏi được bật

        Returns:
            Dict mapping question_type -> số lượng câu hỏi
        """
        num_vocab = len(vocabularies)
        num_types = len(available_types)

        if num_types == 0:
            return {}

        base_count = num_vocab // num_types
        remainder = num_vocab % num_types

        questions_per_type = {}
        for i, q_type in enumerate(available_types):
            count = base_count
            if i < remainder:
                count += 1
            questions_per_type[q_type] = count

        return questions_per_type

    def _create_question(
        self,
        vocabulary: Vocabulary,
        question_type: str,
        all_vocabularies: List[Vocabulary],
    ) -> Dict[str, Any]:
        """
        Tạo một câu hỏi cụ thể sử dụng registry.

        Args:
            vocabulary: Từ vựng chính
            question_type: Loại câu hỏi
            all_vocabularies: Danh sách tất cả từ vựng (để tạo phương án nhiễu)

        Returns:
            Dict chứa thông tin câu hỏi

        Raises:
            ValueError: Nếu question_type không hợp lệ
        """
        question_type_class = self.registry.get(question_type)
        if not question_type_class:
            available_types = ", ".join(self.registry.get_all_types())
            raise ValueError(
                f"Loại câu hỏi không hợp lệ: {question_type}. "
                f"Các loại có sẵn: {available_types}"
            )

        # Một số loại câu hỏi chỉ cần vocabulary chính (writing, speaking)
        # Một số cần thêm pool đáp án nhiễu (listening, reading, matching)
        if question_type_class.requires_pool():
            return question_type_class.build_question(
                vocabulary, all_vocabularies
            )
        else:
            return question_type_class.build_question(vocabulary)

    def evaluate_answer(
        self,
        user_answer: Any,
        question: Dict[str, Any],
        pronunciation_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Đánh giá câu trả lời của người dùng.

        Args:
            user_answer: Câu trả lời của người dùng
            question: Câu hỏi đã được tạo (phải có key "type")
            pronunciation_score: Điểm phát âm (chỉ dùng cho speaking)

        Returns:
            Dict với is_correct, score, feedback

        Raises:
            ValueError: Nếu question_type không hợp lệ
        """
        question_type = question.get("type")
        if not question_type:
            raise ValueError("Câu hỏi phải có key 'type'")

        question_type_class = self.registry.get(question_type)
        if not question_type_class:
            available_types = ", ".join(self.registry.get_all_types())
            raise ValueError(
                f"Loại câu hỏi không hợp lệ: {question_type}. "
                f"Các loại có sẵn: {available_types}"
            )

        return question_type_class.evaluate_answer(
            user_answer, question, pronunciation_score
        )
