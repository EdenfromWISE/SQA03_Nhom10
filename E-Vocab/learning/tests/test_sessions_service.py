"""
learning/tests/test_sessions_service.py
Unit tests cho learning/services/sessions_service.py

Test Cases:
    UT-LRN-SS-001 — create_practice_session: topic rỗng → ValueError
    UT-LRN-SS-002 — create_practice_session: tạo LearningSession + Question hợp lệ
    UT-LRN-SS-003 — create_review_session: không có từ due → ValueError
    UT-LRN-SS-004 — create_review_session: total_questions > 20 → capped 20
    UT-LRN-SS-005 — create_exam_session: vượt max daily exams → ValueError
    UT-LRN-SS-006 — submit_answer: session đã completed → ValueError
    UT-LRN-SS-007 — submit_answer: question_id không thuộc session → ValueError
    UT-LRN-SS-008 — submit_answer: dict answer → lưu vào answer_text
    UT-LRN-SS-009 — submit_answer: int answer → lưu vào selected_option
    UT-LRN-SS-010 — complete_session: tính score đúng, set completed_at và is_passed
    UT-LRN-SS-011 — cancel_session: session đã completed → ValueError
    UT-LRN-SS-012 — complete_session exam: cập nhật UserTopicProgress

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model

from learning.models import LearningConfig, LearningSession, Question, UserAnswer
from learning.services.sessions_service import SessionsService
from progress.models import UserVocabularyMastery, UserTopicProgress
from vocabulary.models import Course, Topic, Vocabulary

User = get_user_model()


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def service():
    """Instance của SessionsService dùng xuyên suốt các test."""
    return SessionsService()


@pytest.fixture
def topic_with_vocab(db):
    """Topic có 5 từ vựng — đủ để tạo session."""
    course = Course.objects.create(title="SS Course")
    topic  = Topic.objects.create(course=course, title="SS Topic")
    for i in range(5):
        Vocabulary.objects.create(
            topic=topic, word=f"word{i}", meaning=f"meaning{i}"
        )
    return topic


@pytest.fixture
def empty_topic(db):
    """Topic không có từ vựng — để kiểm thử lỗi."""
    course = Course.objects.create(title="Empty Course")
    return Topic.objects.create(course=course, title="Empty Topic")


@pytest.fixture
def config(db):
    """LearningConfig singleton với giá trị kiểm thử."""
    cfg = LearningConfig.get_solo()
    cfg.total_questions          = 5
    cfg.pass_score               = 80
    cfg.max_daily_exams_per_topic = 1
    cfg.time_limit               = 10
    cfg.save()
    return cfg


# ══════════════════════════════════════════════════════════════════════════════
# create_practice_session
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCreatePracticeSession:

    # ── UT-LRN-SS-001 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_001_empty_topic_raises_value_error(
        self, service, user, empty_topic, config
    ):
        # TC: UT-LRN-SS-001 — Topic không có từ vựng → Raise ValueError
        # [CheckDB] Xác nhận topic thật sự rỗng
        assert empty_topic.vocabularies.count() == 0

        # [Act & Assert]
        with pytest.raises(ValueError, match="không có từ vựng"):
            service.create_practice_session(user, empty_topic)

        # [CheckDB] Không có LearningSession nào được tạo khi lỗi
        assert LearningSession.objects.filter(user=user).count() == 0

    # ── UT-LRN-SS-002 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_002_creates_session_with_questions(
        self, service, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-002 — create_practice_session tạo LearningSession và Questions trong DB
        # [Act]
        session = service.create_practice_session(user, topic_with_vocab)

        # [Assert] Session được tạo với mode đúng
        assert session.pk is not None
        assert session.mode == "practice"
        assert session.user == user

        # [CheckDB] Session và Questions phải có trong DB
        assert LearningSession.objects.filter(pk=session.pk).exists()
        assert session.questions.count() > 0
        # [Rollback] Session và Questions sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# create_review_session
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCreateReviewSession:

    # ── UT-LRN-SS-003 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_003_no_due_vocab_raises_value_error(self, service, user, config):
        # TC: UT-LRN-SS-003 — Không có từ vựng đến hạn → Raise ValueError
        # [CheckDB] Xác nhận không có UserVocabularyMastery nào đến hạn
        assert UserVocabularyMastery.objects.filter(user=user).count() == 0

        # [Act & Assert]
        with pytest.raises(ValueError, match="không có từ vựng nào đến hạn"):
            service.create_review_session(user)

        # [CheckDB] Không có session được tạo
        assert LearningSession.objects.filter(user=user, mode="review").count() == 0

    # ── UT-LRN-SS-004 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_004_total_questions_capped_at_20(self, service, user, config):
        # TC: UT-LRN-SS-004 — total_questions > 20 → session.total_questions <= 20
        # [Arrange] Tạo 25 từ với mastery đến hạn
        course = Course.objects.create(title="Review Course")
        topic  = Topic.objects.create(course=course, title="Review Topic")
        past   = timezone.now() - timezone.timedelta(days=1)
        for i in range(25):
            v = Vocabulary.objects.create(topic=topic, word=f"rv{i}", meaning=f"m{i}")
            UserVocabularyMastery.objects.create(
                user=user, vocabulary=v, next_review_date=past
            )

        # [CheckDB] Xác nhận 25 mastery đến hạn
        assert UserVocabularyMastery.objects.filter(user=user).count() == 25

        # [Act] Yêu cầu 30 câu (vượt giới hạn 20)
        session = service.create_review_session(user, total_questions=30)

        # [Assert] Phải bị capped tại 20
        assert session.total_questions <= 20, (
            "Review session không được vượt quá 20 câu"
        )

        # [CheckDB] Session đã được tạo trong DB
        assert LearningSession.objects.filter(pk=session.pk).exists()


# ══════════════════════════════════════════════════════════════════════════════
# create_exam_session
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCreateExamSession:

    # ── UT-LRN-SS-005 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_005_max_daily_exams_exceeded_raises_value_error(
        self, service, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-005 — Đã đủ max_daily_exams_per_topic → Raise ValueError
        # [Arrange] Tạo 1 exam session hôm nay (max = 1)
        LearningSession.objects.create(
            user=user,
            topic=topic_with_vocab,
            mode="exam",
            time_limit=10,
            total_questions=5,
            pass_score=80,
            started_at=timezone.now(),
        )

        # [CheckDB] Xác nhận đã có 1 exam hôm nay
        today_exam_count = LearningSession.objects.filter(
            user=user, topic=topic_with_vocab, mode="exam",
            started_at__date=timezone.now().date()
        ).count()
        assert today_exam_count == 1

        # [Act & Assert]
        with pytest.raises(ValueError, match="giới hạn"):
            service.create_exam_session(user, topic_with_vocab)


# ══════════════════════════════════════════════════════════════════════════════
# submit_answer
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestSubmitAnswer:

    def _create_session_with_question(self, user, topic_with_vocab, config):
        """Helper: tạo practice session và trả về (session, question đầu tiên)."""
        svc     = SessionsService()
        session  = svc.create_practice_session(user, topic_with_vocab)
        question = session.questions.first()
        return session, question, svc

    # ── UT-LRN-SS-006 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_006_completed_session_raises_value_error(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-006 — Session đã completed → submit_answer raise ValueError
        # [Arrange] Tạo session rồi đánh dấu completed
        session, question, svc = self._create_session_with_question(
            user, topic_with_vocab, config
        )
        session.completed_at = timezone.now()
        session.save()

        # [CheckDB] Xác nhận session đã completed trong DB
        assert LearningSession.objects.get(pk=session.pk).completed_at is not None

        # [Act & Assert]
        with pytest.raises(ValueError, match="hoàn thành"):
            svc.submit_answer(session, question.id, 0)

    # ── UT-LRN-SS-007 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_007_invalid_question_id_raises_value_error(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-007 — question_id không thuộc session → ValueError
        # [Arrange]
        session, _, svc = self._create_session_with_question(
            user, topic_with_vocab, config
        )
        nonexistent_question_id = 999999  # chắc chắn không tồn tại

        # [Act & Assert]
        with pytest.raises(ValueError, match="không tồn tại"):
            svc.submit_answer(session, nonexistent_question_id, 0)

    # ── UT-LRN-SS-008 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_008_dict_answer_saved_as_answer_text(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-008 — answer kiểu dict → lưu vào answer_text, selected_option=None
        # [Arrange]
        session, question, svc = self._create_session_with_question(
            user, topic_with_vocab, config
        )
        dict_answer = {"key": "value"}  # matching-style answer

        # [Act]
        svc.submit_answer(session, question.id, dict_answer)

        # [CheckDB] Xác nhận UserAnswer được lưu đúng fields
        user_answer = UserAnswer.objects.get(session=session, question=question)
        assert user_answer.answer_text is not None, "dict answer phải lưu vào answer_text"
        assert user_answer.selected_option is None, "selected_option phải None với dict answer"
        # [Rollback] UserAnswer sẽ bị rollback cùng session sau test

    # ── UT-LRN-SS-009 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_009_submit_int_answer_saved_as_selected_option(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-009 — answer kiểu int → lưu vào selected_option, answer_text=None
        # [Arrange] int answer → dùng cho reading/listening (chọn index)
        session, question, svc = self._create_session_with_question(
            user, topic_with_vocab, config
        )

        # [Act]
        svc.submit_answer(session, question.id, 0)

        # [CheckDB] selected_option phải được set, answer_text phải None
        user_answer = UserAnswer.objects.get(session=session, question=question)
        assert user_answer.selected_option is not None
        assert user_answer.answer_text is None
        # [Rollback] UserAnswer sẽ bị rollback cùng session sau test


# ══════════════════════════════════════════════════════════════════════════════
# complete_session / cancel_session
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCompleteAndCancelSession:

    def _make_answered_session(self, user, topic_with_vocab, config):
        """Helper: tạo practice session và trả lời tất cả câu hỏi."""
        svc     = SessionsService()
        session  = svc.create_practice_session(user, topic_with_vocab)
        for q in session.questions.all():
            svc.submit_answer(session, q.id, "word0")  # trả lời dạng string
        return session, svc

    # ── UT-LRN-SS-010 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_010_complete_session_calculates_score_and_sets_completed_at(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-010 — complete_session tính score đúng, set completed_at và is_passed
        # [Arrange]
        session, svc = self._make_answered_session(user, topic_with_vocab, config)
        assert session.completed_at is None  # chưa completed

        # [Act]
        result = svc.complete_session(session)

        # [Assert Response]
        assert result["score"] is not None
        assert 0 <= result["score"] <= 100
        assert "is_passed" in result
        assert result["correct_count"] + (result["total_count"] - result["correct_count"]) \
               == result["total_count"]

        # [CheckDB] completed_at và score phải được persist vào DB
        db_session = LearningSession.objects.get(pk=session.pk)
        assert db_session.completed_at is not None, "completed_at phải được set trong DB"
        assert db_session.score is not None,        "score phải được lưu vào DB"
        # [Rollback] LearningSession changes sẽ bị rollback sau test

    # ── UT-LRN-SS-011 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_011_cancel_completed_session_raises_value_error(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-011 — Hủy session đã hoàn thành → ValueError
        # [Arrange]
        session, svc = self._make_answered_session(user, topic_with_vocab, config)
        svc.complete_session(session)

        # [CheckDB] Xác nhận session đã completed
        assert LearningSession.objects.get(pk=session.pk).completed_at is not None

        # [Act & Assert]
        with pytest.raises(ValueError, match="hoàn thành"):
            svc.cancel_session(session)

        # [CheckDB] Session vẫn tồn tại sau khi cancel thất bại
        assert LearningSession.objects.filter(pk=session.pk).exists()

    # ── UT-LRN-SS-012 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_012_exam_session_updates_user_topic_progress(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-012 — complete_session mode exam → tạo/cập nhật UserTopicProgress
        # [CheckDB] Chưa có UserTopicProgress trước khi thi
        assert not UserTopicProgress.objects.filter(
            user=user, topic=topic_with_vocab
        ).exists()

        # [Arrange] Tạo exam session và trả lời
        svc     = SessionsService()
        session  = svc.create_exam_session(user, topic_with_vocab)
        for q in session.questions.all():
            svc.submit_answer(session, q.id, "word0")

        # [Act]
        svc.complete_session(session)

        # [CheckDB] UserTopicProgress phải được tạo trong DB
        assert UserTopicProgress.objects.filter(
            user=user, topic=topic_with_vocab
        ).exists(), "UserTopicProgress phải được tạo sau khi hoàn thành exam"

        progress = UserTopicProgress.objects.get(user=user, topic=topic_with_vocab)
        assert progress.attempts >= 1, "attempts phải >= 1"
        # [Rollback] UserTopicProgress và LearningSession sẽ bị rollback sau test
