"""
Unit tests for learning/services/question_types/
Covers: ReadingQuestionType, WritingQuestionType, SpeakingQuestionType
"""
import pytest
from unittest.mock import patch, MagicMock

from vocabulary.models import Course, Topic, Vocabulary
from learning.services.question_types.reading import ReadingQuestionType
from learning.services.question_types.writing import WritingQuestionType
from learning.services.question_types.speaking import SpeakingQuestionType


@pytest.fixture
def vocab_pool(db):
    course = Course.objects.create(title="Course")
    topic = Topic.objects.create(course=course, title="Topic")
    words = ["apple", "banana", "cherry", "date", "elderberry"]
    vocabs = []
    for w in words:
        v = Vocabulary.objects.create(topic=topic, word=w, meaning=f"nghia {w}")
        vocabs.append(v)
    return vocabs


@pytest.mark.django_db
class TestReadingQuestionType:

    def test_UT_LRN_QT_READ_001_build_question_creates_valid_structure(self, vocab_pool):
        """UT-LRN-QT-READ-001: build_question tạo cấu trúc hợp lệ với answer là index."""
        target = vocab_pool[0]
        pool = vocab_pool[1:]
        question = ReadingQuestionType.build_question(target, pool)
        assert "id" in question
        assert question["type"] == "reading"
        assert "title" in question
        assert "prompt" in question
        assert "answer" in question
        options = question["prompt"]["options"]
        answer_idx = question["answer"]
        assert 0 <= answer_idx < len(options)
        assert options[answer_idx] == target.word

    def test_UT_LRN_QT_READ_002_evaluate_answer_correct(self, vocab_pool):
        """UT-LRN-QT-READ-002: evaluate_answer đúng → is_correct=True, score=1.0."""
        target = vocab_pool[0]
        question = ReadingQuestionType.build_question(target, vocab_pool[1:])
        correct_idx = question["answer"]
        result = ReadingQuestionType.evaluate_answer(correct_idx, question)
        assert result["is_correct"] is True
        assert result["score"] == 1.0

    def test_UT_LRN_QT_READ_002_evaluate_answer_wrong(self, vocab_pool):
        """UT-LRN-QT-READ-002: evaluate_answer sai → is_correct=False, score=0.0."""
        target = vocab_pool[0]
        question = ReadingQuestionType.build_question(target, vocab_pool[1:])
        correct_idx = question["answer"]
        wrong_idx = (correct_idx + 1) % len(question["prompt"]["options"])
        result = ReadingQuestionType.evaluate_answer(wrong_idx, question)
        assert result["is_correct"] is False
        assert result["score"] == 0.0

    def test_reading_requires_pool(self):
        """ReadingQuestionType.requires_pool() trả True."""
        assert ReadingQuestionType.requires_pool() is True


@pytest.mark.django_db
class TestWritingQuestionType:

    def test_UT_LRN_QT_WR_001_build_question_canonical_is_lowercase_strip(self, vocab_pool):
        """UT-LRN-QT-WR-001: build_question canonical là lowercase/strip."""
        target = vocab_pool[0]  # "apple"
        question = WritingQuestionType.build_question(target)
        canonical = question["answer"]["canonical"]
        assert canonical == target.word.lower().strip()

    def test_UT_LRN_QT_WR_002_evaluate_answer_accepts_case_insensitive(self, vocab_pool):
        """UT-LRN-QT-WR-002: evaluate_answer chấp nhận biến thể hoa/thường."""
        target = vocab_pool[0]  # "apple"
        question = WritingQuestionType.build_question(target)
        result = WritingQuestionType.evaluate_answer("APPLE", question)
        assert result["is_correct"] is True

    def test_evaluate_writing_wrong_answer(self, vocab_pool):
        """evaluate_answer trả sai với từ không đúng."""
        target = vocab_pool[0]
        question = WritingQuestionType.build_question(target)
        result = WritingQuestionType.evaluate_answer("wrongword", question)
        assert result["is_correct"] is False
        assert result["score"] == 0.0

    def test_writing_not_requires_pool(self):
        """WritingQuestionType.requires_pool() trả False."""
        assert WritingQuestionType.requires_pool() is False


def _mock_assessor(assessor_obj=None):
    """Helper: trả context manager mock app config với pronunciation_assessor."""
    mock_cfg = MagicMock()
    mock_cfg.pronunciation_assessor = assessor_obj
    return patch(
        "learning.services.question_types.speaking.apps.get_app_config",
        return_value=mock_cfg,
    )


@pytest.mark.django_db
class TestSpeakingQuestionType:

    # ── assessor = None ──────────────────────────────────

    def test_UT_LRN_QT_SPK_001_evaluate_returns_false_when_assessor_none(self, vocab_pool):
        """UT-LRN-QT-SPK-001: assessor=None → is_correct=False, feedback hệ thống."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(None):
            result = SpeakingQuestionType.evaluate_answer("anything", question)
        assert result["is_correct"] is False
        assert "chưa sẵn sàng" in result["feedback"]

    # ── assessor có sẵn + float score ───────────────────

    def test_evaluate_float_answer_above_threshold_is_correct(self, vocab_pool):
        """float user_answer >= 70 → is_correct=True, score chuẩn hoá."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(85.0, question)
        assert result["is_correct"] is True
        assert abs(result["score"] - 0.85) < 0.001
        assert result["pronunciation_score"] == 85.0

    def test_evaluate_float_answer_below_threshold_is_wrong(self, vocab_pool):
        """float user_answer < 70 → is_correct=False."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(50.0, question)
        assert result["is_correct"] is False

    def test_evaluate_int_answer_treated_as_score(self, vocab_pool):
        """int user_answer cũng được xử lý như float score."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(75, question)
        assert result["is_correct"] is True

    # ── assessor có sẵn + dict user_answer ──────────────

    def test_evaluate_dict_with_pronunciation_score(self, vocab_pool):
        """dict chứa 'pronunciation_score' → dùng score đó để đánh giá."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        user_answer = {"pronunciation_score": 92.0, "phonemes": [{"p": "æ", "score": 0.9}]}
        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(user_answer, question)
        assert result["is_correct"] is True
        assert "phonemes" in result

    def test_evaluate_dict_without_valid_key_returns_invalid_format(self, vocab_pool):
        """dict không có 'pronunciation_score' hay 'audio_file' → invalid format."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer({"unknown": "val"}, question)
        assert result["is_correct"] is False
        assert "không hợp lệ" in result["feedback"]

    def test_evaluate_invalid_type_returns_error(self, vocab_pool):
        """user_answer kiểu list/None → trả lỗi 'phải là file audio'."""
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(["wrong"], question)
        assert result["is_correct"] is False
        assert "file audio" in result["feedback"]

    # ── _get_feedback trực tiếp ──────────────────────────

    def test_get_feedback_excellent(self):
        assert "xuất sắc" in SpeakingQuestionType._get_feedback(95)

    def test_get_feedback_very_good(self):
        assert "rất tốt" in SpeakingQuestionType._get_feedback(82)

    def test_get_feedback_good(self):
        assert "khá tốt" in SpeakingQuestionType._get_feedback(70)

    def test_get_feedback_needs_improvement(self):
        assert "cần cải thiện" in SpeakingQuestionType._get_feedback(55)

    def test_get_feedback_incorrect(self):
        assert "chưa chính xác" in SpeakingQuestionType._get_feedback(30)

    # ── deprecated wrappers ──────────────────────────────

    def test_deprecated_build_question_wrapper(self, vocab_pool):
        """Module-level build_question() gọi đúng class method."""
        from learning.services.question_types.speaking import build_question
        target = vocab_pool[0]
        q = build_question(target)
        assert q["type"] == "speaking"

    def test_deprecated_evaluate_answer_wrapper(self, vocab_pool):
        """Module-level evaluate_answer() gọi đúng class method."""
        from learning.services.question_types.speaking import evaluate_answer
        target = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)
        with _mock_assessor(None):
            result = evaluate_answer("x", question)
        assert result["is_correct"] is False
