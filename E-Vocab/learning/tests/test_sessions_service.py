"""
Unit tests for learning/services/sessions_service.py
Covers: SessionsService - create_practice_session, create_review_session,
        create_exam_session, submit_answer, complete_session, cancel_session
"""
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model

from learning.models import LearningConfig, LearningSession, Question, UserAnswer
from learning.services.sessions_service import SessionsService
from progress.models import UserVocabularyMastery, UserTopicProgress
from vocabulary.models import Course, Topic, Vocabulary

User = get_user_model()


@pytest.fixture
def service():
    return SessionsService()


@pytest.fixture
def topic_with_vocab(db):
    course = Course.objects.create(title="SS Course")
    topic = Topic.objects.create(course=course, title="SS Topic")
    for i in range(5):
        Vocabulary.objects.create(
            topic=topic, word=f"word{i}", meaning=f"meaning{i}"
        )
    return topic


@pytest.fixture
def empty_topic(db):
    course = Course.objects.create(title="Empty Course")
    return Topic.objects.create(course=course, title="Empty Topic")


@pytest.fixture
def config(db):
    cfg = LearningConfig.get_solo()
    cfg.total_questions = 5
    cfg.pass_score = 80
    cfg.max_daily_exams_per_topic = 1
    cfg.time_limit = 10
    cfg.save()
    return cfg


# ─────────────────────────────────────────────────────────
# create_practice_session
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCreatePracticeSession:

    def test_UT_LRN_SS_001_empty_topic_raises_value_error(self, service, user, empty_topic, config):
        """UT-LRN-SS-001: Topic không có từ → Raise ValueError."""
        with pytest.raises(ValueError, match="không có từ vựng"):
            service.create_practice_session(user, empty_topic)

    def test_creates_session_with_questions(self, service, user, topic_with_vocab, config):
        """create_practice_session tạo LearningSession và Questions thành công."""
        session = service.create_practice_session(user, topic_with_vocab)
        assert session.pk is not None
        assert session.mode == "practice"
        assert session.user == user
        assert session.questions.count() > 0


# ─────────────────────────────────────────────────────────
# create_review_session
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateReviewSession:

    def test_UT_LRN_SS_002_no_due_vocab_raises_value_error(self, service, user, config):
        """UT-LRN-SS-002: Không có từ đến hạn → Raise ValueError."""
        with pytest.raises(ValueError, match="không có từ vựng nào đến hạn"):
            service.create_review_session(user)

    def test_UT_LRN_SS_003_total_questions_capped_at_20(self, service, user, config):
        """UT-LRN-SS-003: total_questions > 20 → session.total_questions <= 20."""
        course = Course.objects.create(title="Review Course")
        topic = Topic.objects.create(course=course, title="Review Topic")
        past = timezone.now() - timezone.timedelta(days=1)
        for i in range(25):
            v = Vocabulary.objects.create(topic=topic, word=f"rv{i}", meaning=f"m{i}")
            UserVocabularyMastery.objects.create(
                user=user, vocabulary=v, next_review_date=past
            )
        session = service.create_review_session(user, total_questions=30)
        assert session.total_questions <= 20


# ─────────────────────────────────────────────────────────
# create_exam_session
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateExamSession:

    def test_UT_LRN_SS_004_max_daily_exams_exceeded_raises_value_error(
        self, service, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-004: Đã đủ max_daily_exams_per_topic → Raise ValueError."""
        LearningSession.objects.create(
            user=user,
            topic=topic_with_vocab,
            mode="exam",
            time_limit=10,
            total_questions=5,
            pass_score=80,
            started_at=timezone.now(),
        )
        with pytest.raises(ValueError, match="giới hạn"):
            service.create_exam_session(user, topic_with_vocab)


# ─────────────────────────────────────────────────────────
# submit_answer
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSubmitAnswer:

    def _make_session_with_question(self, user, topic_with_vocab, config):
        service = SessionsService()
        session = service.create_practice_session(user, topic_with_vocab)
        question = session.questions.first()
        return session, question

    def test_UT_LRN_SS_005_completed_session_raises_value_error(
        self, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-005: Session đã completed → Raise ValueError."""
        session, question = self._make_session_with_question(user, topic_with_vocab, config)
        session.completed_at = timezone.now()
        session.save()
        with pytest.raises(ValueError, match="hoàn thành"):
            SessionsService().submit_answer(session, question.id, 0)

    def test_UT_LRN_SS_006_invalid_question_id_raises_value_error(
        self, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-006: question_id không thuộc session → Raise ValueError."""
        session, _ = self._make_session_with_question(user, topic_with_vocab, config)
        with pytest.raises(ValueError, match="không tồn tại"):
            SessionsService().submit_answer(session, 999999, 0)

    def test_UT_LRN_SS_007_dict_answer_saved_as_answer_text(
        self, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-007: answer kiểu dict → answer_text được set, selected_option None."""
        session, question = self._make_session_with_question(user, topic_with_vocab, config)
        SessionsService().submit_answer(session, question.id, {"key": "val"})
        ua = UserAnswer.objects.get(session=session, question=question)
        assert ua.answer_text is not None
        assert ua.selected_option is None

    def test_submit_int_answer_saved_as_selected_option(
        self, user, topic_with_vocab, config
    ):
        """answer kiểu int → selected_option được set."""
        session, question = self._make_session_with_question(user, topic_with_vocab, config)
        SessionsService().submit_answer(session, question.id, 0)
        ua = UserAnswer.objects.get(session=session, question=question)
        assert ua.selected_option is not None


# ─────────────────────────────────────────────────────────
# complete_session / cancel_session
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCompleteAndCancelSession:

    def _make_and_answer_session(self, user, topic_with_vocab, config):
        svc = SessionsService()
        session = svc.create_practice_session(user, topic_with_vocab)
        for q in session.questions.all():
            svc.submit_answer(session, q.id, "word0")
        return session, svc

    def test_UT_LRN_SS_008_complete_session_calculates_score_and_sets_completed_at(
        self, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-008: complete_session tính score, set completed_at và is_passed."""
        session, svc = self._make_and_answer_session(user, topic_with_vocab, config)
        result = svc.complete_session(session)
        assert result["score"] is not None
        assert 0 <= result["score"] <= 100
        session.refresh_from_db()
        assert session.completed_at is not None
        assert "is_passed" in result

    def test_UT_LRN_SS_009_cancel_completed_session_raises_value_error(
        self, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-009: cancel session đã hoàn thành → Raise ValueError."""
        session, svc = self._make_and_answer_session(user, topic_with_vocab, config)
        svc.complete_session(session)
        with pytest.raises(ValueError, match="hoàn thành"):
            svc.cancel_session(session)

    def test_UT_LRN_SS_010_exam_session_updates_user_topic_progress(
        self, user, topic_with_vocab, config
    ):
        """UT-LRN-SS-010: complete_session mode exam cập nhật UserTopicProgress."""
        svc = SessionsService()
        session = svc.create_exam_session(user, topic_with_vocab)
        for q in session.questions.all():
            svc.submit_answer(session, q.id, "word0")
        svc.complete_session(session)
        assert UserTopicProgress.objects.filter(user=user, topic=topic_with_vocab).exists()
