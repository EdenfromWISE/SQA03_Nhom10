"""
Question type: Reading - Đọc nghĩa và chọn từ tiếng Anh tương ứng.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary
from .base import QuestionTypeBase


class ReadingQuestionType(QuestionTypeBase):
    """Câu hỏi đọc nghĩa và chọn từ tiếng Anh tương ứng."""
    
    QUESTION_TYPE = "reading"
    DISPLAY_NAME = "Đọc nghĩa và chọn từ"
    
    @classmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        options: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo câu hỏi reading: đọc nghĩa và chọn từ tiếng Anh tương ứng.
        
        Args:
            vocabulary: Từ vựng chính
            pool: Danh sách từ vựng để tạo phương án nhiễu
            options: Số lượng phương án (mặc định 4)
        """
        if pool is None:
            pool = []
        
        distractors = cls._pick_word_distractors(vocabulary, pool, options - 1)
        choices = [vocabulary.word, *distractors]
        random.shuffle(choices)
        
        question_data = {
            "id": f"def_word_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Chọn từ tiếng Anh tương ứng với nghĩa",
            "prompt": {
                "definition": vocabulary.meaning,
                "options": choices,
            },
            "answer": choices.index(vocabulary.word),
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
        Đánh giá câu trả lời reading.
        
        Args:
            user_answer: Index của phương án được chọn (int)
            question: Câu hỏi đã được tạo
            pronunciation_score: Không sử dụng trong reading
        """
        correct_answer = question.get("answer")
        is_correct = isinstance(user_answer, int) and user_answer == correct_answer
        
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Giỏi lắm!" if is_correct else "Sai đáp án, hãy đọc kỹ nghĩa.",
        }
    
    @classmethod
    def requires_pool(cls) -> bool:
        """Reading cần pool để tạo phương án nhiễu."""
        return True
    
    @classmethod
    def _pick_word_distractors(
        cls, target: Vocabulary, pool: List[Vocabulary], count: int
    ) -> List[str]:
        """Tạo các phương án nhiễu cho từ - ưu tiên độ dài tương tự."""
        # Lọc ra các từ có độ dài tương tự
        candidates = [
            v
            for v in pool
            if v.id != target.id
            and abs(len(v.word) - len(target.word)) <= 2
        ]
        
        if len(candidates) < count:
            # Nếu không đủ, lấy thêm từ khác
            other_candidates = [v for v in pool if v.id != target.id]
            candidates.extend(other_candidates)
        
        selected = random.sample(candidates, min(count, len(candidates)))
        return [v.word for v in selected]


# Giữ lại các hàm cũ để tương thích ngược (deprecated)
QUESTION_TYPE = ReadingQuestionType.QUESTION_TYPE


def build_question(vocabulary: Vocabulary, pool: List[Vocabulary], options: int = 4) -> Dict[str, Any]:
    """Deprecated: Sử dụng ReadingQuestionType.build_question thay thế."""
    return ReadingQuestionType.build_question(vocabulary, pool, options=options)


def evaluate_answer(user_answer: Any, question: Dict[str, Any]) -> Dict[str, Any]:
    """Deprecated: Sử dụng ReadingQuestionType.evaluate_answer thay thế."""
    return ReadingQuestionType.evaluate_answer(user_answer, question)
