"""
Unit tests for learning/services/question_service.py
Covers: QuestionService.generate_session_questions, evaluate_answer,
        get_available_question_types
"""
import pytest

from vocabulary.models import Course, Topic, Vocabulary
from learning.services.question_service import QuestionService


@pytest.fixture
def question_service():
    return QuestionService()


@pytest.fixture
def vocab_list(db):
    course = Course.objects.create(title="QS Course")
    topic = Topic.objects.create(course=course, title="QS Topic")
    vocabs = []
    for i in range(10):
        v = Vocabulary.objects.create(
            topic=topic, word=f"word{i}", meaning=f"nghia{i}"
        )
        vocabs.append(v)
    return vocabs


@pytest.mark.django_db
class TestGenerateSessionQuestions:

    def test_UT_LRN_QS_001_empty_vocabularies_raises_value_error(self, question_service):
        """UT-LRN-QS-001: vocabularies=[] → Raise ValueError."""
        with pytest.raises(ValueError, match="rỗng"):
            question_service.generate_session_questions(vocabularies=[])

    def test_UT_LRN_QS_002_invalid_enabled_type_raises_value_error(
        self, question_service, vocab_list
    ):
        """UT-LRN-QS-002: enabled_types chứa type lạ → Raise ValueError."""
        with pytest.raises(ValueError):
            question_service.generate_session_questions(
                vocabularies=vocab_list, enabled_types=["nonexistent_type"]
            )

    def test_generates_questions_for_all_vocabs_by_default(
        self, question_service, vocab_list
    ):
        """Mặc định tạo câu hỏi đúng số vocab."""
        questions = question_service.generate_session_questions(vocabularies=vocab_list)
        assert len(questions) == len(vocab_list)

    def test_respects_total_questions_limit(self, question_service, vocab_list):
        """total_questions giới hạn số câu hỏi tạo ra."""
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, total_questions=3
        )
        assert len(questions) == 3

    def test_generates_with_single_enabled_type(self, question_service, vocab_list):
        """enabled_types=['writing'] → chỉ tạo writing questions."""
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, enabled_types=["writing"]
        )
        assert all(q["type"] == "writing" for q in questions)


@pytest.mark.django_db
class TestEvaluateAnswer:

    def test_UT_LRN_QS_003_question_without_type_raises_value_error(self, question_service):
        """UT-LRN-QS-003: question dict không có key 'type' → Raise ValueError."""
        with pytest.raises(ValueError, match="type"):
            question_service.evaluate_answer(user_answer="abc", question={"answer": "something"})

    def test_evaluate_reading_correct_answer(self, question_service, vocab_list):
        """Reading question: đúng đáp án → is_correct=True."""
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, enabled_types=["reading"]
        )
        q = questions[0]
        correct_answer = q["answer"]
        result = question_service.evaluate_answer(user_answer=correct_answer, question=q)
        assert result["is_correct"] is True

    def test_evaluate_writing_correct_answer(self, question_service, vocab_list):
        """Writing question: đúng đáp án → is_correct=True."""
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, enabled_types=["writing"]
        )
        q = questions[0]
        canonical = q["answer"]["canonical"]
        result = question_service.evaluate_answer(user_answer=canonical, question=q)
        assert result["is_correct"] is True


class TestGetAvailableQuestionTypes:

    def test_UT_LRN_QS_004_returns_all_standard_types(self, question_service):
        """UT-LRN-QS-004: get_available_question_types trả map có các type chuẩn."""
        types = question_service.get_available_question_types()
        assert isinstance(types, dict)
        for expected in ("reading", "writing", "listening", "matching", "speaking"):
            assert expected in types, f"Missing type: {expected}"
