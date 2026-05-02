"""
learning/tests/test_question_types.py
Unit tests cho learning/services/question_types/

Test Cases:
    UT-LRN-QT-READ-001 — ReadingQuestionType.build_question: cấu trúc hợp lệ
    UT-LRN-QT-READ-002 — ReadingQuestionType.evaluate_answer: đáp án đúng → score=1.0
    UT-LRN-QT-READ-003 — ReadingQuestionType.evaluate_answer: đáp án sai → score=0.0
    UT-LRN-QT-READ-004 — ReadingQuestionType.requires_pool() trả True
    UT-LRN-QT-WR-001   — WritingQuestionType.build_question: canonical là lowercase/strip
    UT-LRN-QT-WR-002   — WritingQuestionType.evaluate_answer: chấp nhận case insensitive
    UT-LRN-QT-WR-003   — WritingQuestionType.evaluate_answer: từ sai → score=0.0
    UT-LRN-QT-WR-004   — WritingQuestionType.requires_pool() trả False
    UT-LRN-QT-SPK-001  — SpeakingQuestionType.evaluate_answer: assessor=None → False
    UT-LRN-QT-SPK-002  — SpeakingQuestionType.evaluate_answer: float >= 70 → True
    UT-LRN-QT-SPK-003  — SpeakingQuestionType.evaluate_answer: float < 70 → False
    UT-LRN-QT-SPK-004  — SpeakingQuestionType.evaluate_answer: int treated as score
    UT-LRN-QT-SPK-005  — SpeakingQuestionType.evaluate_answer: dict có pronunciation_score
    UT-LRN-QT-SPK-006  — SpeakingQuestionType.evaluate_answer: dict không hợp lệ
    UT-LRN-QT-SPK-007  — SpeakingQuestionType.evaluate_answer: kiểu list/None → invalid
    UT-LRN-QT-SPK-008  — SpeakingQuestionType._get_feedback: score>=90 → 'xuất sắc'
    UT-LRN-QT-SPK-009  — SpeakingQuestionType._get_feedback: score>=80 → 'rất tốt'
    UT-LRN-QT-SPK-010  — SpeakingQuestionType._get_feedback: score>=70 → 'khá tốt'
    UT-LRN-QT-SPK-011  — SpeakingQuestionType._get_feedback: score>=50 → 'cần cải thiện'
    UT-LRN-QT-SPK-012  — SpeakingQuestionType._get_feedback: score<50 → 'chưa chính xác'
    UT-LRN-QT-SPK-013  — Module-level build_question() delegate sang class method
    UT-LRN-QT-SPK-014  — Module-level evaluate_answer() delegate sang class method

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from unittest.mock import patch, MagicMock

from vocabulary.models import Course, Topic, Vocabulary
from learning.services.question_types.reading  import ReadingQuestionType
from learning.services.question_types.writing  import WritingQuestionType
from learning.services.question_types.speaking import SpeakingQuestionType


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def vocab_pool(db):
    """5 từ vựng — đủ pool cho ReadingQuestionType (cần ít nhất 4 lựa chọn)."""
    course = Course.objects.create(title="Course")
    topic  = Topic.objects.create(course=course, title="Topic")
    vocabs = []
    for w in ["apple", "banana", "cherry", "date", "elderberry"]:
        v = Vocabulary.objects.create(topic=topic, word=w, meaning=f"nghia {w}")
        vocabs.append(v)
    return vocabs


# ── Helper ─────────────────────────────────────────────────────────────────────

def _mock_assessor(assessor_obj=None):
    """Patch apps.get_app_config để trả mock PronunciationAssessor."""
    mock_cfg = MagicMock()
    mock_cfg.pronunciation_assessor = assessor_obj
    return patch(
        "learning.services.question_types.speaking.apps.get_app_config",
        return_value=mock_cfg,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ReadingQuestionType
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestReadingQuestionType:

    # ── UT-LRN-QT-READ-001 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_READ_001_build_question_creates_valid_structure(self, vocab_pool):
        # TC: UT-LRN-QT-READ-001 — build_question tạo cấu trúc hợp lệ với answer là index
        # [Arrange] target là từ đầu, pool là phần còn lại
        target = vocab_pool[0]
        pool   = vocab_pool[1:]

        # [CheckDB] Xác nhận vocabulary tồn tại trong DB
        assert Vocabulary.objects.filter(pk=target.pk).exists()

        # [Act]
        question = ReadingQuestionType.build_question(target, pool)

        # [Assert] Cấu trúc đúng fields, answer index trỏ đúng word trong options
        assert "id"     in question
        assert question["type"] == "reading"
        assert "title"  in question
        assert "prompt" in question
        assert "answer" in question
        options    = question["prompt"]["options"]
        answer_idx = question["answer"]
        assert 0 <= answer_idx < len(options), "answer index phải nằm trong range options"
        assert options[answer_idx] == target.word, "options[answer] phải là word của target"
        # [Rollback] Vocabulary sẽ bị rollback sau test

    # ── UT-LRN-QT-READ-002 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_READ_002_evaluate_answer_correct(self, vocab_pool):
        # TC: UT-LRN-QT-READ-002 — evaluate_answer đúng → is_correct=True, score=1.0
        # [Arrange]
        target      = vocab_pool[0]
        question    = ReadingQuestionType.build_question(target, vocab_pool[1:])
        correct_idx = question["answer"]

        # [Act]
        result = ReadingQuestionType.evaluate_answer(correct_idx, question)

        # [Assert]
        assert result["is_correct"] is True
        assert result["score"] == 1.0

    # ── UT-LRN-QT-READ-003 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_READ_003_evaluate_answer_wrong(self, vocab_pool):
        # TC: UT-LRN-QT-READ-003 — evaluate_answer index sai → is_correct=False, score=0.0
        # [Arrange] Chọn index sai (cộng 1 rồi mod)
        target      = vocab_pool[0]
        question    = ReadingQuestionType.build_question(target, vocab_pool[1:])
        correct_idx = question["answer"]
        wrong_idx   = (correct_idx + 1) % len(question["prompt"]["options"])

        # [Act]
        result = ReadingQuestionType.evaluate_answer(wrong_idx, question)

        # [Assert]
        assert result["is_correct"] is False
        assert result["score"] == 0.0

    # ── UT-LRN-QT-READ-004 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_READ_004_reading_requires_pool(self):
        # TC: UT-LRN-QT-READ-004 — ReadingQuestionType.requires_pool() trả True (cần pool sinh options)
        # [Act & Assert] ReadingQuestionType cần pool để tạo options
        assert ReadingQuestionType.requires_pool() is True


# ══════════════════════════════════════════════════════════════════════════════
# WritingQuestionType
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestWritingQuestionType:

    # ── UT-LRN-QT-WR-001 ──────────────────────────────────────────────────
    def test_UT_LRN_QT_WR_001_build_question_canonical_is_lowercase_strip(self, vocab_pool):
        # TC: UT-LRN-QT-WR-001 — build_question canonical là word.lower().strip()
        # [Arrange] target word = "apple"
        target = vocab_pool[0]

        # [Act]
        question  = WritingQuestionType.build_question(target)
        canonical = question["answer"]["canonical"]

        # [Assert] canonical là lowercase và trimmed
        assert canonical == target.word.lower().strip()

    # ── UT-LRN-QT-WR-002 ──────────────────────────────────────────────────
    def test_UT_LRN_QT_WR_002_evaluate_answer_accepts_case_insensitive(self, vocab_pool):
        # TC: UT-LRN-QT-WR-002 — evaluate_answer chấp nhận biến thể hoa/thường
        # [Arrange] target = "apple"
        target   = vocab_pool[0]
        question = WritingQuestionType.build_question(target)

        # [Act] Gửi "APPLE" (uppercase)
        result = WritingQuestionType.evaluate_answer("APPLE", question)

        # [Assert] Phải được chấp nhận (case insensitive)
        assert result["is_correct"] is True

    # ── UT-LRN-QT-WR-003 ──────────────────────────────────────────────────
    def test_UT_LRN_QT_WR_003_evaluate_writing_wrong_answer(self, vocab_pool):
        # TC: UT-LRN-QT-WR-003 — evaluate_answer với từ sai → is_correct=False, score=0.0
        # [Arrange]
        target   = vocab_pool[0]
        question = WritingQuestionType.build_question(target)

        # [Act] Gửi từ hoàn toàn sai
        result = WritingQuestionType.evaluate_answer("wrongword", question)

        # [Assert]
        assert result["is_correct"] is False
        assert result["score"] == 0.0

    # ── UT-LRN-QT-WR-004 ──────────────────────────────────────────────────
    def test_UT_LRN_QT_WR_004_writing_not_requires_pool(self):
        # TC: UT-LRN-QT-WR-004 — WritingQuestionType.requires_pool() trả False (không có multiple choice)
        # [Act & Assert] WritingQuestionType không cần pool (không có multiple choice)
        assert WritingQuestionType.requires_pool() is False


# ══════════════════════════════════════════════════════════════════════════════
# SpeakingQuestionType
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestSpeakingQuestionType:

    # ── UT-LRN-QT-SPK-001 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_001_evaluate_returns_false_when_assessor_none(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-001 — assessor=None → is_correct=False, feedback "chưa sẵn sàng"
        # [Arrange]
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        # [Act] Mock assessor = None (tính năng phát âm chưa được kích hoạt)
        with _mock_assessor(None):
            result = SpeakingQuestionType.evaluate_answer("anything", question)

        # [Assert]
        assert result["is_correct"] is False
        assert "chưa sẵn sàng" in result["feedback"]

    # ── UT-LRN-QT-SPK-002 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_002_evaluate_float_answer_above_threshold_is_correct(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-002 — float score >= 70 → is_correct=True, score chuẩn hoá, pronunciation_score được set
        # [Arrange] float score >= 70 → pass
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        with _mock_assessor(MagicMock()):
            # [Act]
            result = SpeakingQuestionType.evaluate_answer(85.0, question)

        # [Assert] is_correct=True, score chuẩn hoá, pronunciation_score được set
        assert result["is_correct"] is True
        assert abs(result["score"] - 0.85) < 0.001
        assert result["pronunciation_score"] == 85.0

    # ── UT-LRN-QT-SPK-003 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_003_evaluate_float_answer_below_threshold_is_wrong(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-003 — float score < 70 → is_correct=False
        # [Arrange] float score < 70 → fail
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(50.0, question)

        assert result["is_correct"] is False

    # ── UT-LRN-QT-SPK-004 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_004_evaluate_int_answer_treated_as_score(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-004 — int answer cũng được xử lý như float score
        # [Arrange] int answer cũng được xử lý như float score
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(75, question)

        assert result["is_correct"] is True

    # ── UT-LRN-QT-SPK-005 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_005_evaluate_dict_with_pronunciation_score(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-005 — dict có 'pronunciation_score' → dùng score đó để đánh giá
        # [Arrange] dict có key 'pronunciation_score' → dùng score đó
        target      = vocab_pool[0]
        question    = SpeakingQuestionType.build_question(target)
        user_answer = {"pronunciation_score": 92.0, "phonemes": [{"p": "æ", "score": 0.9}]}

        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(user_answer, question)

        assert result["is_correct"] is True
        assert "phonemes" in result

    # ── UT-LRN-QT-SPK-006 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_006_evaluate_dict_without_valid_key_returns_invalid_format(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-006 — dict không có 'pronunciation_score'/'audio_file' → định dạng không hợp lệ
        # [Arrange] dict không có 'pronunciation_score' hay 'audio_file' → định dạng không hợp lệ
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer({"unknown": "val"}, question)

        assert result["is_correct"] is False
        assert "không hợp lệ" in result["feedback"]

    # ── UT-LRN-QT-SPK-007 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_007_evaluate_invalid_type_returns_error(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-007 — user_answer kiểu list/None → trả lỗi 'phải là file audio'
        # [Arrange] user_answer kiểu list → không hợp lệ
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        with _mock_assessor(MagicMock()):
            result = SpeakingQuestionType.evaluate_answer(["wrong"], question)

        assert result["is_correct"] is False
        assert "file audio" in result["feedback"]

    # ── _get_feedback branches ─────────────────────────────────────────────

    # ── UT-LRN-QT-SPK-008 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_008_get_feedback_excellent(self):
        # TC: UT-LRN-QT-SPK-008 — score >= 90 → feedback "xuất sắc"
        # [Act & Assert] score >= 90 → "xuất sắc"
        assert "xuất sắc" in SpeakingQuestionType._get_feedback(95)

    # ── UT-LRN-QT-SPK-009 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_009_get_feedback_very_good(self):
        # TC: UT-LRN-QT-SPK-009 — score >= 80 → feedback "rất tốt"
        # [Act & Assert] score >= 80 → "rất tốt"
        assert "rất tốt" in SpeakingQuestionType._get_feedback(82)

    # ── UT-LRN-QT-SPK-010 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_010_get_feedback_good(self):
        # TC: UT-LRN-QT-SPK-010 — score >= 70 → feedback "khá tốt"
        # [Act & Assert] score >= 70 → "khá tốt"
        assert "khá tốt" in SpeakingQuestionType._get_feedback(70)

    # ── UT-LRN-QT-SPK-011 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_011_get_feedback_needs_improvement(self):
        # TC: UT-LRN-QT-SPK-011 — score >= 50 → feedback "cần cải thiện"
        # [Act & Assert] score >= 50 → "cần cải thiện"
        assert "cần cải thiện" in SpeakingQuestionType._get_feedback(55)

    # ── UT-LRN-QT-SPK-012 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_012_get_feedback_incorrect(self):
        # TC: UT-LRN-QT-SPK-012 — score < 50 → feedback "chưa chính xác"
        # [Act & Assert] score < 50 → "chưa chính xác"
        assert "chưa chính xác" in SpeakingQuestionType._get_feedback(30)

    # ── deprecated module-level wrappers ──────────────────────────────────

    # ── UT-LRN-QT-SPK-013 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_013_deprecated_build_question_wrapper(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-013 — Module-level build_question() delegate sang class method
        # [Arrange] Module-level build_question() nên delegate sang class method
        from learning.services.question_types.speaking import build_question
        target = vocab_pool[0]

        # [Act & Assert]
        q = build_question(target)
        assert q["type"] == "speaking"

    # ── UT-LRN-QT-SPK-014 ─────────────────────────────────────────────────
    def test_UT_LRN_QT_SPK_014_deprecated_evaluate_answer_wrapper(self, vocab_pool):
        # TC: UT-LRN-QT-SPK-014 — Module-level evaluate_answer() delegate sang class method
        # [Arrange] Module-level evaluate_answer() nên delegate sang class method
        from learning.services.question_types.speaking import evaluate_answer
        target   = vocab_pool[0]
        question = SpeakingQuestionType.build_question(target)

        with _mock_assessor(None):
            result = evaluate_answer("x", question)

        assert result["is_correct"] is False
