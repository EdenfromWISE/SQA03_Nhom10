"""
progress/tests/test_srs_service.py
Unit tests cho progress/services/srs_service.py (thuật toán SM-2)

Test Cases:
    UT-PRG-SM2-001 — is_vocabulary_eligible: từ mới chưa có mastery → True
    UT-PRG-SM2-002 — update_review: chưa đến hạn, không force → trả None
    UT-PRG-SM2-003 — update_review: trả lời đúng → repetitions tăng, interval tăng
    UT-PRG-SM2-004 — update_review: trả lời sai → repetitions=0, interval=1
    UT-PRG-SM2-005 — get_vocabularies_due_for_review: chỉ trả từ đến hạn, đúng thứ tự

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from progress.models import UserVocabularyMastery
from progress.services.srs_service import SM2Service
from vocabulary.models import Course, Topic, Vocabulary

User = get_user_model()


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def vocab(db):
    """Từ vựng đơn lẻ dùng trong các test SM-2."""
    course = Course.objects.create(title="SRS Course")
    topic  = Topic.objects.create(course=course, title="SRS Topic")
    return Vocabulary.objects.create(topic=topic, word="apple", meaning="quả táo")


@pytest.fixture
def vocab2(db):
    """Từ vựng thứ hai để test multi-vocab scenarios."""
    course = Course.objects.get_or_create(title="SRS Course")[0]
    topic  = Topic.objects.get_or_create(course=course, title="SRS Topic")[0]
    return Vocabulary.objects.create(topic=topic, word="banana", meaning="quả chuối")


# ══════════════════════════════════════════════════════════════════════════════
# is_vocabulary_eligible_for_srs
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestIsVocabularyEligibleForSrs:
    """Kiểm thử điều kiện đủ điều kiện để ghi nhận SRS."""

    # ── UT-PRG-SM2-001 ─────────────────────────────────────────────────────
    def test_UT_PRG_SM2_001_new_vocab_without_mastery_is_eligible(self, user, vocab):
        # TC: UT-PRG-SM2-001 — Từ mới, chưa có mastery → eligible = True
        # [CheckDB] Xác nhận chưa có mastery trong DB
        assert not UserVocabularyMastery.objects.filter(
            user=user, vocabulary=vocab
        ).exists()

        # [Act]
        result = SM2Service.is_vocabulary_eligible_for_srs(user, vocab)

        # [Assert]
        assert result is True

    def test_vocab_with_null_next_review_is_eligible(self, user, vocab):
        # [Arrange] Tạo mastery với next_review_date=None (từ mới học chưa lên lịch)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=None
        )

        # [CheckDB] Xác nhận mastery đã tạo
        assert UserVocabularyMastery.objects.filter(
            user=user, vocabulary=vocab, next_review_date__isnull=True
        ).exists()

        # [Act & Assert]
        assert SM2Service.is_vocabulary_eligible_for_srs(user, vocab) is True

    def test_vocab_not_yet_due_is_not_eligible(self, user, vocab):
        # [Arrange] next_review_date trong tương lai → chưa đến hạn
        future = timezone.now() + timedelta(days=5)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=future
        )

        # [Act & Assert]
        assert SM2Service.is_vocabulary_eligible_for_srs(user, vocab) is False


# ══════════════════════════════════════════════════════════════════════════════
# update_review
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestUpdateReview:
    """Kiểm thử SM2Service.update_review — cập nhật interval/repetitions."""

    # ── UT-PRG-SM2-002 ─────────────────────────────────────────────────────
    def test_UT_PRG_SM2_002_update_review_returns_none_when_not_due(self, user, vocab):
        # TC: UT-PRG-SM2-002 — Chưa đến hạn, force_update=False → trả None
        # [Arrange] next_review_date 3 ngày nữa
        future = timezone.now() + timedelta(days=3)
        mastery_before = UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=future, repetitions=2
        )
        initial_repetitions = mastery_before.repetitions

        # [Act]
        result = SM2Service.update_review(user, vocab, is_correct=True, force_update=False)

        # [Assert] Trả None, không cập nhật
        assert result is None

        # [CheckDB] Mastery KHÔNG thay đổi trong DB
        mastery_after = UserVocabularyMastery.objects.get(user=user, vocabulary=vocab)
        assert mastery_after.repetitions == initial_repetitions

    # ── UT-PRG-SM2-003 ─────────────────────────────────────────────────────
    def test_UT_PRG_SM2_003_correct_answer_increases_repetitions_and_interval(
        self, user, vocab
    ):
        # TC: UT-PRG-SM2-003 — Trả lời đúng → repetitions tăng, interval tăng, EF >= 1.3
        # [Arrange] repetitions=2 → sẽ vào nhánh else: interval = int(interval * ef)
        past = timezone.now() - timedelta(days=1)
        initial_interval    = 6
        initial_repetitions = 2
        initial_ef          = 2.5
        UserVocabularyMastery.objects.create(
            user=user,
            vocabulary=vocab,
            repetitions=initial_repetitions,
            interval=initial_interval,
            ease_factor=initial_ef,
            next_review_date=past,
        )

        # [Act]
        result = SM2Service.update_review(user, vocab, is_correct=True)

        # [Assert]
        assert result is not None
        assert result.repetitions == initial_repetitions + 1
        assert result.interval == int(initial_interval * initial_ef)
        assert result.ease_factor >= 1.3, "EF phải >= 1.3 theo quy tắc SM-2"

        # [CheckDB] Giá trị đã được persist vào DB
        db_mastery = UserVocabularyMastery.objects.get(user=user, vocabulary=vocab)
        assert db_mastery.repetitions == initial_repetitions + 1
        assert db_mastery.correct_count == 1

    # ── UT-PRG-SM2-004 ─────────────────────────────────────────────────────
    def test_UT_PRG_SM2_004_wrong_answer_resets_repetitions_and_interval(
        self, user, vocab
    ):
        # TC: UT-PRG-SM2-004 — Trả lời sai → repetitions=0, interval=1
        # [Arrange] User có streak dài, trả lời sai sẽ reset về đầu
        past = timezone.now() - timedelta(days=1)
        UserVocabularyMastery.objects.create(
            user=user,
            vocabulary=vocab,
            repetitions=5,
            interval=30,
            ease_factor=2.5,
            next_review_date=past,
        )

        # [Act]
        result = SM2Service.update_review(user, vocab, is_correct=False)

        # [Assert] Reset về giá trị đầu theo SM-2
        assert result is not None
        assert result.repetitions == 0, "Sai → repetitions reset về 0"
        assert result.interval == 1,    "Sai → interval reset về 1 ngày"

        # [CheckDB] DB phải reflect reset
        db_mastery = UserVocabularyMastery.objects.get(user=user, vocabulary=vocab)
        assert db_mastery.repetitions == 0
        assert db_mastery.incorrect_count == 1

    def test_ease_factor_clamped_at_1_3_minimum(self, user, vocab):
        # [Arrange] EF thấp, trả lời sai nhiều lần → EF không được < 1.3
        past = timezone.now() - timedelta(days=1)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, ease_factor=1.31, next_review_date=past
        )

        # [Act]
        result = SM2Service.update_review(user, vocab, is_correct=False)

        # [Assert] EF bị clamp tại 1.3
        assert result.ease_factor >= 1.3


# ══════════════════════════════════════════════════════════════════════════════
# get_vocabularies_due_for_review
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestGetVocabulariesDueForReview:
    """Kiểm thử SM2Service.get_vocabularies_due_for_review."""

    # ── UT-PRG-SM2-005 ─────────────────────────────────────────────────────
    def test_UT_PRG_SM2_005_returns_only_due_vocabularies_in_order(
        self, user, vocab, vocab2
    ):
        # TC: UT-PRG-SM2-005 — Chỉ trả mastery đến hạn, đúng thứ tự next_review_date
        # [Arrange] Tạo 3 mastery: 2 quá hạn (thứ tự khác nhau) + 1 chưa đến hạn
        now    = timezone.now()
        past1  = now - timedelta(days=2)  # quá hạn nhất
        past2  = now - timedelta(days=1)  # quá hạn gần hơn
        future = now + timedelta(days=5)  # chưa đến hạn

        # vocab → past1 (quá hạn hơn → phải đứng trước)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=past1
        )
        # vocab2 → future (chưa đến hạn → không được trả)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab2, next_review_date=future
        )
        # vocab3 → past2 (quá hạn ít hơn → đứng sau vocab)
        course = Course.objects.get_or_create(title="SRS Course")[0]
        topic  = Topic.objects.get_or_create(course=course, title="SRS Topic")[0]
        vocab3 = Vocabulary.objects.create(
            topic=topic, word="cherry", meaning="quả anh đào"
        )
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab3, next_review_date=past2
        )

        # [CheckDB] Xác nhận có 3 mastery trong DB
        assert UserVocabularyMastery.objects.filter(user=user).count() == 3

        # [Act]
        due_list = SM2Service.get_vocabularies_due_for_review(user)

        # [Assert] Chỉ trả 2 mastery đến hạn, đúng thứ tự ascending
        due_vocab_ids = [m.vocabulary_id for m in due_list]
        assert vocab.id  in due_vocab_ids, "vocab (past1) phải trong due list"
        assert vocab3.id in due_vocab_ids, "vocab3 (past2) phải trong due list"
        assert vocab2.id not in due_vocab_ids, "vocab2 (future) KHÔNG được trong due list"

        # Thứ tự: oldest due first
        assert due_list[0].vocabulary_id == vocab.id,  "vocab phải đứng trước (quá hạn hơn)"
        assert due_list[1].vocabulary_id == vocab3.id, "vocab3 đứng sau"
