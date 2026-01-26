"""
Question type: Writing - Đọc nghĩa và nhập từ tiếng Anh tương ứng.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary
from .base import QuestionTypeBase


class WritingQuestionType(QuestionTypeBase):
    """Câu hỏi đọc nghĩa và nhập từ tiếng Anh tương ứng."""
    
    QUESTION_TYPE = "writing"
    DISPLAY_NAME = "Đọc nghĩa và nhập từ"
    
    @classmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo câu hỏi writing: đọc nghĩa và nhập từ tiếng Anh tương ứng.
        
        Args:
            vocabulary: Từ vựng chính
            pool: Không sử dụng trong writing (có thể None)
        """
        canonical = vocabulary.word.lower().strip()
        alternatives = cls._generate_variants(canonical)
        
        question_data = {
            "id": f"def_input_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Nhập từ tiếng Anh tương ứng với nghĩa",
            "prompt": {
                "definition": vocabulary.meaning,
                "hint": f"Từ có {len(canonical)} chữ cái, bắt đầu bằng '{canonical[0].upper()}'",
            },
            "answer": {
                "canonical": canonical,
                "alternatives": alternatives,
            },
            "explanation": f"'{vocabulary.meaning}' có nghĩa là '{vocabulary.word}'",
            "metadata": {"vocabulary_id": vocabulary.id},
        }
        
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
        Đánh giá câu trả lời writing.
        
        Args:
            user_answer: Từ người dùng nhập (str)
            question: Câu hỏi đã được tạo
            pronunciation_score: Không sử dụng trong writing
        """
        if not isinstance(user_answer, str):
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Câu trả lời phải là chuỗi.",
            }
        
        normalized = user_answer.lower().strip()
        answer_data = question.get("answer", {})
        valid = [answer_data.get("canonical", ""), *answer_data.get("alternatives", [])]
        is_correct = normalized in valid
        
        canonical = answer_data.get("canonical", "")
        
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Chuẩn xác!" if is_correct else f"Đáp án đúng là '{canonical}'.",
        }
    
    @classmethod
    def requires_pool(cls) -> bool:
        """Writing không cần pool để tạo phương án nhiễu."""
        return False
    
    @classmethod
    def _generate_variants(cls, word: str) -> List[str]:
        """Tạo các biến thể của từ (singular/plural, verb forms, etc.)."""
        variants = {word}
        if word.endswith("s"):
            variants.add(word[:-1])
        if word.endswith("ed"):
            variants.add(word[:-2])
        if word.endswith("ing"):
            variants.add(word[:-3])
        return list(variants)


# Giữ lại các hàm cũ để tương thích ngược (deprecated)
QUESTION_TYPE = WritingQuestionType.QUESTION_TYPE


def build_question(vocabulary: Vocabulary) -> Dict[str, Any]:
    """Deprecated: Sử dụng WritingQuestionType.build_question thay thế."""
    return WritingQuestionType.build_question(vocabulary)


def evaluate_answer(user_answer: Any, question: Dict[str, Any]) -> Dict[str, Any]:
    """Deprecated: Sử dụng WritingQuestionType.evaluate_answer thay thế."""
    return WritingQuestionType.evaluate_answer(user_answer, question)
