"""
Question type: Matching - Ghép cặp từ với nghĩa tương ứng.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary
from .base import QuestionTypeBase


class MatchingQuestionType(QuestionTypeBase):
    """Câu hỏi ghép cặp từ với nghĩa tương ứng."""
    
    QUESTION_TYPE = "matching"
    DISPLAY_NAME = "Ghép cặp từ với nghĩa"
    
    @classmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        pairs: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo câu hỏi matching: ghép cặp từ với nghĩa tương ứng.
        
        Args:
            vocabulary: Từ vựng chính
            pool: Danh sách từ vựng để tạo các cặp khác
            pairs: Số lượng cặp (mặc định 4)
        """
        if pool is None:
            pool = []
        
        available = [v for v in pool if v.id != vocabulary.id]
        selected = [vocabulary] + random.sample(
            available, min(pairs - 1, len(available))
        )
        
        words = [v.word for v in selected]
        definitions = [v.meaning for v in selected]
        
        # Trộn thứ tự nghĩa, đảm bảo không có cặp nào nằm cùng vị trí
        shuffled_definitions = definitions[:]
        while True:
            random.shuffle(shuffled_definitions)
            has_same_position = any(
                words[i] == selected[j].word
                and shuffled_definitions[i] == selected[j].meaning
                for i in range(len(words))
                for j in range(len(selected))
            )
            if not has_same_position:
                break
        
        correct_mapping = {w: d for w, d in zip(words, definitions)}
        
        question_data = {
            "id": f"matching_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Ghép cặp từ với nghĩa tương ứng",
            "prompt": {
                "words": words,
                "definitions": shuffled_definitions,
            },
            "answer": correct_mapping,
            "explanation": "Ghép đúng từ với nghĩa tương ứng",
            "metadata": {"vocabulary_ids": [v.id for v in selected]},
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
        Đánh giá câu trả lời matching.
        
        Args:
            user_answer: Dict mapping word -> definition
            question: Câu hỏi đã được tạo
            pronunciation_score: Không sử dụng trong matching
        """
        if not isinstance(user_answer, dict):
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Câu trả lời phải là mapping word→definition.",
            }
        
        correct_answer = question.get("answer", {})
        total = len(correct_answer)
        
        if total == 0:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Câu hỏi không hợp lệ.",
            }
        
        correct = sum(
            1 for word, definition in correct_answer.items()
            if user_answer.get(word) == definition
        )
        score = round(correct / total, 2)
        
        return {
            "is_correct": score == 1.0,
            "score": score,
            "feedback": f"Đúng {correct}/{total} cặp.",
        }
    
    @classmethod
    def requires_pool(cls) -> bool:
        """Matching cần pool để tạo các cặp từ-nghĩa."""
        return True


# Giữ lại các hàm cũ để tương thích ngược (deprecated)
QUESTION_TYPE = MatchingQuestionType.QUESTION_TYPE


def build_question(vocabulary: Vocabulary, pool: List[Vocabulary], pairs: int = 4) -> Dict[str, Any]:
    """Deprecated: Sử dụng MatchingQuestionType.build_question thay thế."""
    return MatchingQuestionType.build_question(vocabulary, pool, pairs=pairs)


def evaluate_answer(user_answer: Any, question: Dict[str, Any]) -> Dict[str, Any]:
    """Deprecated: Sử dụng MatchingQuestionType.evaluate_answer thay thế."""
    return MatchingQuestionType.evaluate_answer(user_answer, question)
