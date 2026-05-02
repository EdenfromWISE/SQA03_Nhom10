"""
learning/tests/test_question_service.py
Unit tests cho learning/services/question_service.py

Test Cases:
    UT-LRN-QS-001 — generate_session_questions: vocabularies=[] → ValueError
    UT-LRN-QS-002 — generate_session_questions: enabled_types chứa type lạ → ValueError
    UT-LRN-QS-003 — generate_session_questions: mặc định tạo câu hỏi đúng số vocab
    UT-LRN-QS-004 — generate_session_questions: total_questions giới hạn số câu hỏi
    UT-LRN-QS-005 — generate_session_questions: enabled_types=['writing'] → tất cả writing
    UT-LRN-QS-006 — evaluate_answer: question không có key 'type' → ValueError
    UT-LRN-QS-007 — evaluate_answer: reading đúng đáp án → is_correct=True
    UT-LRN-QS-008 — evaluate_answer: writing đúng đáp án → is_correct=True
    UT-LRN-QS-009 — get_available_question_types: trả map có 5 type chuẩn

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary
from learning.services.question_service import QuestionService


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def question_service():
    """Instance QuestionService dùng xuyên suốt các test."""
    return QuestionService()


@pytest.fixture
def vocab_list(db):
    """10 từ vựng — đủ để test các trường hợp generate_session_questions."""
    course = Course.objects.create(title="QS Course")
    topic  = Topic.objects.create(course=course, title="QS Topic")
    vocabs = []
    for i in range(10):
        v = Vocabulary.objects.create(
            topic=topic, word=f"word{i}", meaning=f"nghia{i}"
        )
        vocabs.append(v)
    return vocabs


# ══════════════════════════════════════════════════════════════════════════════
# generate_session_questions
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestGenerateSessionQuestions:

    # ── UT-LRN-QS-001 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_001_empty_vocabularies_raises_value_error(self, question_service):
        # TC: UT-LRN-QS-001 — vocabularies=[] → Raise ValueError chứa "rỗng"
        # [Arrange] List vocabularies rỗng
        # [Act & Assert]
        with pytest.raises(ValueError, match="rỗng"):
            question_service.generate_session_questions(vocabularies=[])

    # ── UT-LRN-QS-002 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_002_invalid_enabled_type_raises_value_error(
        self, question_service, vocab_list
    ):
        # TC: UT-LRN-QS-002 — enabled_types chứa type không tồn tại → Raise ValueError
        # [CheckDB] Xác nhận vocab_list đã có trong DB
        assert Vocabulary.objects.count() == 10

        # [Act & Assert]
        with pytest.raises(ValueError):
            question_service.generate_session_questions(
                vocabularies=vocab_list, enabled_types=["nonexistent_type"]
            )

    # ── UT-LRN-QS-003 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_003_generates_questions_for_all_vocabs_by_default(
        self, question_service, vocab_list
    ):
        # TC: UT-LRN-QS-003 — Mặc định tạo đúng 1 câu hỏi cho mỗi vocab
        # [Arrange] 10 vocabularies, không giới hạn total_questions
        # [Act]
        questions = question_service.generate_session_questions(vocabularies=vocab_list)

        # [Assert] Mỗi vocab cho 1 question
        assert len(questions) == len(vocab_list)

    # ── UT-LRN-QS-004 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_004_respects_total_questions_limit(self, question_service, vocab_list):
        # TC: UT-LRN-QS-004 — total_questions=3 → chỉ tạo 3 câu hỏi (giới hạn)
        # [Arrange] total_questions = 3 (nhỏ hơn số vocab)
        # [Act]
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, total_questions=3
        )

        # [Assert] Phải giới hạn đúng 3 câu
        assert len(questions) == 3

    # ── UT-LRN-QS-005 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_005_generates_with_single_enabled_type(self, question_service, vocab_list):
        # TC: UT-LRN-QS-005 — enabled_types=['writing'] → tất cả câu hỏi đều type='writing'
        # [Arrange] Chỉ bật type 'writing'
        # [Act]
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, enabled_types=["writing"]
        )

        # [Assert] Tất cả question phải type=writing
        assert all(q["type"] == "writing" for q in questions), (
            "Khi enabled_types=['writing'], tất cả câu phải là writing"
        )


# ══════════════════════════════════════════════════════════════════════════════
# evaluate_answer
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestEvaluateAnswer:

    # ── UT-LRN-QS-006 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_006_question_without_type_raises_value_error(self, question_service):
        # TC: UT-LRN-QS-006 — question dict không có key 'type' → Raise ValueError
        # [Arrange] question dict thiếu key 'type'
        bad_question = {"answer": "something"}

        # [Act & Assert]
        with pytest.raises(ValueError, match="type"):
            question_service.evaluate_answer(user_answer="abc", question=bad_question)

    # ── UT-LRN-QS-007 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_007_evaluate_reading_correct_answer(self, question_service, vocab_list):
        # TC: UT-LRN-QS-007 — Reading question, đúng đáp án → is_correct=True
        # [Arrange] Tạo reading question, lấy đáp án đúng
        questions   = question_service.generate_session_questions(
            vocabularies=vocab_list, enabled_types=["reading"]
        )
        q           = questions[0]
        correct_ans = q["answer"]

        # [Act]
        result = question_service.evaluate_answer(user_answer=correct_ans, question=q)

        # [Assert]
        assert result["is_correct"] is True

    # ── UT-LRN-QS-008 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_008_evaluate_writing_correct_answer(self, question_service, vocab_list):
        # TC: UT-LRN-QS-008 — Writing question, đúng canonical → is_correct=True
        # [Arrange] Tạo writing question, lấy canonical làm đáp án
        questions = question_service.generate_session_questions(
            vocabularies=vocab_list, enabled_types=["writing"]
        )
        q         = questions[0]
        canonical = q["answer"]["canonical"]

        # [Act]
        result = question_service.evaluate_answer(user_answer=canonical, question=q)

        # [Assert]
        assert result["is_correct"] is True
        # [Rollback] Vocabulary sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# get_available_question_types
# ══════════════════════════════════════════════════════════════════════════════

class TestGetAvailableQuestionTypes:

    # ── UT-LRN-QS-009 ─────────────────────────────────────────────────────
    def test_UT_LRN_QS_009_returns_all_standard_types(self, question_service):
        # TC: UT-LRN-QS-009 — get_available_question_types trả map có 5 type chuẩn
        # [Act]
        types = question_service.get_available_question_types()

        # [Assert] Phải là dict chứa đủ 5 type
        assert isinstance(types, dict)
        for expected in ("reading", "writing", "listening", "matching", "speaking"):
            assert expected in types, f"get_available_question_types thiếu type: {expected}"
