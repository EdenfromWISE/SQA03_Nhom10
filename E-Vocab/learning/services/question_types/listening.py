"""
Question type: Listening - Nghe và chọn nghĩa đúng của từ.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from vocabulary.models import Vocabulary
from .base import QuestionTypeBase


class ListeningQuestionType(QuestionTypeBase):
    """Câu hỏi nghe và chọn nghĩa đúng của từ."""
    
    QUESTION_TYPE = "listening"
    DISPLAY_NAME = "Nghe và chọn nghĩa"
    
    @classmethod
    def build_question(
        cls,
        vocabulary: Vocabulary,
        pool: Optional[List[Vocabulary]] = None,
        options: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo câu hỏi listening: nghe audio và chọn nghĩa đúng.
        
        Args:
            vocabulary: Từ vựng chính
            pool: Danh sách từ vựng để tạo phương án nhiễu
            options: Số lượng phương án (mặc định 4)
        """
        if pool is None:
            pool = []
        
        distractors = cls._pick_meaning_distractors(vocabulary, pool, options - 1)
        choices = [vocabulary.meaning, *distractors]
        random.shuffle(choices)
        
        question_data = {
            "id": f"audio_mc_{vocabulary.id}",
            "type": cls.QUESTION_TYPE,
            "title": "Nghe và chọn nghĩa đúng của từ",
            "prompt": {
                "word": vocabulary.word,
                "audio_url": vocabulary.audio_url or "",
                "pronunciation": vocabulary.pronunciation or "",
                "options": choices,
            },
            "answer": choices.index(vocabulary.meaning),
            "explanation": f"Từ '{vocabulary.word}' có nghĩa là '{vocabulary.meaning}'",
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
        Đánh giá câu trả lời listening.
        
        Args:
            user_answer: Index của phương án được chọn (int)
            question: Câu hỏi đã được tạo
            pronunciation_score: Không sử dụng trong listening
        """
        correct_answer = question.get("answer")
        is_correct = isinstance(user_answer, int) and user_answer == correct_answer
        
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Chính xác!" if is_correct else "Chưa đúng, hãy nghe lại audio.",
        }
    
    @classmethod
    def requires_pool(cls) -> bool:
        """Listening cần pool để tạo phương án nhiễu."""
        return True
    
    @classmethod
    def _pick_meaning_distractors(
        cls, target: Vocabulary, pool: List[Vocabulary], count: int
    ) -> List[str]:
        """Tạo các phương án nhiễu cho nghĩa - ưu tiên cùng loại từ."""
        # Lọc ra các từ khác cùng loại từ
        candidates = [
            v
            for v in pool
            if v.id != target.id and v.word_type == target.word_type
        ]
        
        if len(candidates) < count:
            # Nếu không đủ, lấy thêm từ khác loại
            other_candidates = [
                v
                for v in pool
                if v.id != target.id and v.word_type != target.word_type
            ]
            candidates.extend(other_candidates)
        
        selected = random.sample(candidates, min(count, len(candidates)))
        return [v.meaning for v in selected]


# Giữ lại các hàm cũ để tương thích ngược (deprecated)
QUESTION_TYPE = ListeningQuestionType.QUESTION_TYPE


def build_question(vocabulary: Vocabulary, pool: List[Vocabulary], options: int = 4) -> Dict[str, Any]:
    """Deprecated: Sử dụng ListeningQuestionType.build_question thay thế."""
    return ListeningQuestionType.build_question(vocabulary, pool, options=options)


def evaluate_answer(user_answer: Any, question: Dict[str, Any]) -> Dict[str, Any]:
    """Deprecated: Sử dụng ListeningQuestionType.evaluate_answer thay thế."""
    return ListeningQuestionType.evaluate_answer(user_answer, question)
