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
    UT-LRN-SS-013 — UC6: create_practice_session với question_distribution → các câu hỏi đúng phân phối
    UT-LRN-SS-014 — UC6: complete_session practice (pass_score=0) → is_passed=True
    UT-LRN-SS-015 — UC8: create_exam_session happy path → tạo session với mode/time_limit/pass_score đúng
    UT-LRN-SS-016 — UC8: create_exam_session với topic rỗng → ValueError
    UT-LRN-SS-017 — UC8: complete_session exam đạt pass_score → is_passed=True, best_score cập nhật
    UT-LRN-SS-018 — UC8: complete_session exam dưới pass_score → is_passed=False, best_score=0
    UT-LRN-SS-019 — UC8 E1 (spec): cancel_session chưa completed → lưu bài kiểm tra 0 điểm
    UT-LRN-SS-020 — UC6 ĐK1 (spec): topic < 5 từ vựng → ValueError "tối thiểu 5"
    UT-LRN-SS-021 — UC8 ĐK1 (spec): chưa học đủ 20 từ → ValueError "tối thiểu 20"
    UT-LRN-SS-022 — UC8 (spec): default time_limit của LearningConfig phải = 20 phút

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


# ══════════════════════════════════════════════════════════════════════════════
# UC6 (Practice) — bổ sung
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestPracticeUseCase6:
    """Bổ sung kiểm thử cho UC06 — Practice (Luyện tập)."""

    # ── UT-LRN-SS-013 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_013_practice_with_question_distribution_creates_correct_mix(
        self, service, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-013 — UC6: chọn nhiều mode (vd Write + Reading) → các câu hỏi tạo ra
        # phải đúng theo question_distribution đã chỉ định
        # [Arrange] Yêu cầu 3 câu writing + 2 câu reading
        distribution = {"writing": 3, "reading": 2}

        # [Act]
        session = service.create_practice_session(
            user, topic_with_vocab,
            total_questions=5,
            question_distribution=distribution,
        )

        # [Assert] Session là practice
        assert session.mode == "practice"
        assert session.total_questions == 5

        # [CheckDB] Mỗi loại câu hỏi xuất hiện đúng theo distribution
        types = list(session.questions.values_list("question_type", flat=True))
        assert types.count("writing") == 3, f"Phải có 3 writing, nhưng có {types.count('writing')}"
        assert types.count("reading") == 2, f"Phải có 2 reading, nhưng có {types.count('reading')}"
        # [Rollback] Session + Questions sẽ bị rollback sau test

    # ── UT-LRN-SS-014 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_014_complete_practice_session_always_passes(
        self, service, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-014 — UC6: Practice luôn có pass_score=0 nên is_passed=True
        # bất kể đúng/sai (Practice không cần đạt điểm tối thiểu)
        # [Arrange] Tạo practice session, KHÔNG trả lời câu nào (score sẽ = 0)
        session = service.create_practice_session(user, topic_with_vocab)

        # [CheckDB] pass_score của practice phải = 0
        assert session.pass_score == 0, "Practice session pass_score phải = 0"

        # [Act] Hoàn thành mà không trả lời gì
        result = service.complete_session(session)

        # [Assert] score=0 vẫn is_passed=True (vì pass_score=0)
        assert result["score"] == 0
        assert result["is_passed"] is True, "Practice với pass_score=0 phải luôn is_passed=True"

        # [CheckDB] DB cũng phải reflect is_passed=True
        db_session = LearningSession.objects.get(pk=session.pk)
        assert db_session.is_passed is True
        # [Rollback] Session sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# UC8 (Take Exam) — bổ sung
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestExamUseCase8:
    """Bổ sung kiểm thử cho UC08 — Take Exam (Làm bài kiểm tra)."""

    # ── UT-LRN-SS-015 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_015_create_exam_session_happy_path(
        self, service, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-015 — UC8 happy path: tạo exam session đầu tiên
        # → mode='exam', time_limit/pass_score lấy từ config, có Questions
        # [CheckDB] Trước khi tạo: chưa có exam session nào hôm nay
        assert LearningSession.objects.filter(
            user=user, topic=topic_with_vocab, mode="exam"
        ).count() == 0

        # [Act]
        session = service.create_exam_session(user, topic_with_vocab)

        # [Assert] Tất cả field theo đúng spec UC8
        assert session.pk is not None
        assert session.mode == "exam"
        assert session.user == user
        assert session.topic == topic_with_vocab
        assert session.time_limit == config.time_limit, "time_limit phải lấy từ config"
        assert session.pass_score == config.pass_score, "pass_score phải lấy từ config"
        assert session.completed_at is None, "Session mới tạo chưa completed"

        # [CheckDB] Session + Questions phải được lưu vào DB
        assert LearningSession.objects.filter(pk=session.pk, mode="exam").exists()
        assert session.questions.count() > 0, "Phải có ít nhất 1 question"
        # [Rollback] Session + Questions sẽ bị rollback sau test

    # ── UT-LRN-SS-016 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_016_create_exam_session_with_empty_topic_raises_value_error(
        self, service, user, empty_topic, config
    ):
        # TC: UT-LRN-SS-016 — UC8 negative: topic không có từ vựng → ValueError
        # [Arrange] empty_topic là topic không có Vocabulary nào
        assert Vocabulary.objects.filter(topic=empty_topic).count() == 0

        # [Act & Assert]
        with pytest.raises(ValueError, match="không có từ vựng"):
            service.create_exam_session(user, empty_topic)

        # [CheckDB] Không có exam session nào được tạo
        assert LearningSession.objects.filter(
            user=user, topic=empty_topic, mode="exam"
        ).count() == 0

    # ── UT-LRN-SS-017 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_017_complete_exam_passing_score_marks_passed_and_updates_best(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-017 — UC8: complete exam với điểm >= pass_score
        # → is_passed=True và UserTopicProgress.best_score được cập nhật
        # [Arrange] Tạo exam, trả lời ĐÚNG hết (vì test data dùng word0..word4 và
        # writing question chấp nhận đúng từ → score = 100)
        svc      = SessionsService()
        session  = svc.create_exam_session(user, topic_with_vocab)

        # Trả lời mọi câu bằng đáp án đúng — lấy correct_answer cho từng question
        for q in session.questions.all():
            # writing có correct_answer = {"canonical": ...}, reading có int index
            ca = q.correct_answer
            if isinstance(ca, dict) and "canonical" in ca:
                svc.submit_answer(session, q.id, ca["canonical"])
            else:
                svc.submit_answer(session, q.id, ca)

        # [Act]
        result = svc.complete_session(session)

        # [Assert Response] score >= pass_score → is_passed=True
        assert result["score"] >= session.pass_score, (
            f"Test setup sai: score={result['score']} < pass_score={session.pass_score}"
        )
        assert result["is_passed"] is True

        # [CheckDB] UserTopicProgress.best_score được cập nhật và is_passed=True
        progress = UserTopicProgress.objects.get(user=user, topic=topic_with_vocab)
        assert progress.is_passed is True, "UserTopicProgress.is_passed phải True"
        assert progress.best_score == result["score"], (
            f"best_score phải = score đạt ({result['score']}), nhưng nhận {progress.best_score}"
        )
        # [Rollback] Session + Progress sẽ bị rollback sau test

    # ── UT-LRN-SS-018 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_018_complete_exam_failing_score_keeps_best_score_zero(
        self, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-018 — UC8: complete exam với điểm < pass_score (config 80)
        # → is_passed=False, UserTopicProgress.best_score giữ 0 (không tính điểm rớt)
        # [Arrange] Tạo exam, KHÔNG trả lời gì → score = 0 < pass_score=80
        svc     = SessionsService()
        session = svc.create_exam_session(user, topic_with_vocab)

        # [Act] Hoàn thành mà không trả lời câu nào
        result = svc.complete_session(session)

        # [Assert] score=0, is_passed=False
        assert result["score"] == 0
        assert result["is_passed"] is False, "score=0 < pass_score=80 → is_passed phải False"

        # [CheckDB] UserTopicProgress phải tạo nhưng best_score giữ 0
        progress = UserTopicProgress.objects.get(user=user, topic=topic_with_vocab)
        assert progress.attempts == 1
        assert progress.is_passed is False, "UserTopicProgress.is_passed phải False"
        assert progress.best_score == 0, (
            f"best_score phải giữ 0 khi rớt, nhưng nhận {progress.best_score}"
        )
        # [Rollback] Session + Progress sẽ bị rollback sau test

    # ── UT-LRN-SS-019 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_019_cancel_uncompleted_exam_saves_zero_score(
        self, service, user, topic_with_vocab, config
    ):
        # TC: UT-LRN-SS-019 — UC8 E1 (spec):
        #   "Hủy bài kiểm tra và thoát: hệ thống lưu bài kiểm tra 0 điểm"
        # → Sau cancel, session phải VẪN còn trong DB với score=0,
        #   completed_at được set, is_passed=False.
        # [Bug expected] Code hiện tại dùng `session.delete()` → test sẽ FAIL,
        #   bóc lộ sai lệch giữa code và đặc tả.
        # [Arrange] Tạo exam session
        session    = service.create_exam_session(user, topic_with_vocab)
        session_pk = session.pk

        # [CheckDB] Trước khi cancel: session tồn tại, chưa completed
        assert LearningSession.objects.filter(pk=session_pk).exists()
        assert session.completed_at is None

        # [Act]
        service.cancel_session(session)

        # [CheckDB per spec] Session phải VẪN còn trong DB sau cancel
        assert LearningSession.objects.filter(pk=session_pk).exists(), (
            "Spec UC8 E1: hủy thi phải LƯU bài, không được xoá khỏi DB."
        )

        # [Assert per spec] Score = 0, đã đóng phiên, không pass
        db_session = LearningSession.objects.get(pk=session_pk)
        assert db_session.score == 0, (
            f"Spec UC8 E1: bài bị hủy phải lưu 0 điểm, nhận {db_session.score}"
        )
        assert db_session.completed_at is not None, (
            "Spec UC8 E1: cancel phải đóng phiên (set completed_at)"
        )
        assert db_session.is_passed is False, (
            "Spec UC8 E1: bài 0 điểm không thể là is_passed=True"
        )
        # [Rollback] Session sẽ bị rollback sau test

    # ── UT-LRN-SS-020 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_020_practice_with_less_than_5_vocab_raises(
        self, service, user, config
    ):
        # TC: UT-LRN-SS-020 — UC6 ĐK1 (spec):
        #   "Chọn tối thiểu 5 từ" → topic có 4 từ phải bị từ chối.
        # [Bug expected] Code hiện chỉ check `not vocabularies` (rỗng),
        #   không check ngưỡng 5 → test sẽ FAIL, bóc lộ thiếu kiểm tra ràng buộc.
        # [Arrange] Topic có 4 từ (< 5)
        course = Course.objects.create(title="UC6 Course")
        topic  = Topic.objects.create(course=course, title="UC6 Topic")
        for i in range(4):
            Vocabulary.objects.create(topic=topic, word=f"w{i}", meaning=f"m{i}")

        # [CheckDB] Xác nhận chỉ có 4 từ
        assert Vocabulary.objects.filter(topic=topic).count() == 4

        # [Act & Assert per spec] phải raise vì < 5 từ
        with pytest.raises(ValueError, match=r"(tối thiểu 5|ít nhất 5)"):
            service.create_practice_session(user, topic)

        # [CheckDB] Không có session nào được tạo
        assert LearningSession.objects.filter(user=user, topic=topic).count() == 0

    # ── UT-LRN-SS-021 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_021_exam_requires_20_learned_vocab(
        self, service, user, config
    ):
        # TC: UT-LRN-SS-021 — UC8 ĐK1 (spec):
        #   "Minimum 20 từ đã học" mới được thi.
        # [Bug expected] Code chỉ check topic không rỗng, không check số từ "đã học"
        #   trên user → test sẽ FAIL, bóc lộ thiếu ràng buộc.
        # [Arrange] Topic có 25 từ nhưng user chỉ "đã học" 19 từ
        course = Course.objects.create(title="UC8 Course")
        topic  = Topic.objects.create(course=course, title="UC8 Topic")
        vocabs = [
            Vocabulary.objects.create(topic=topic, word=f"e{i}", meaning=f"m{i}")
            for i in range(25)
        ]
        # User chỉ học 19 từ (UserVocabularyMastery dùng để đánh dấu đã học)
        for v in vocabs[:19]:
            UserVocabularyMastery.objects.create(
                user=user, vocabulary=v,
                next_review_date=timezone.now(),
            )

        # [CheckDB] Xác nhận user mới học 19 từ
        assert UserVocabularyMastery.objects.filter(user=user).count() == 19

        # [Act & Assert per spec]
        with pytest.raises(ValueError, match=r"(tối thiểu 20|ít nhất 20|20 từ đã học)"):
            service.create_exam_session(user, topic)

    # ── UT-LRN-SS-022 ──────────────────────────────────────────────────────
    def test_UT_LRN_SS_022_default_exam_time_limit_is_20_minutes(self, db):
        # TC: UT-LRN-SS-022 — UC8 spec: "Thời gian thi: 20 phút"
        #   → LearningConfig.time_limit mặc định phải = 20.
        # [Bug expected] Code hiện đặt default=10 (learning/models.py:12) → FAIL.
        # [Arrange & Act] Lấy config singleton ở trạng thái mặc định
        cfg = LearningConfig.get_solo()

        # [Assert per spec]
        assert cfg.time_limit == 20, (
            f"Spec UC8: thi 20 phút; default code đặt {cfg.time_limit} phút."
        )
