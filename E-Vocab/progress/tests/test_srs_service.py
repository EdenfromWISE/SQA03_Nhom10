"""
Unit tests for progress/services/srs_service.py
Covers: SM2Service - is_vocabulary_eligible_for_srs, update_review,
        get_vocabularies_due_for_review, get_new_vocabularies
"""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from progress.models import UserVocabularyMastery
from progress.services.srs_service import SM2Service
from vocabulary.models import Course, Topic, Vocabulary

User = get_user_model()


@pytest.fixture
def vocab(db):
    course = Course.objects.create(title="Test Course")
    topic = Topic.objects.create(course=course, title="Test Topic")
    return Vocabulary.objects.create(topic=topic, word="apple", meaning="quả táo")


@pytest.fixture
def vocab2(db):
    course = Course.objects.get_or_create(title="Test Course")[0]
    topic = Topic.objects.get_or_create(course=course, title="Test Topic")[0]
    return Vocabulary.objects.create(topic=topic, word="banana", meaning="quả chuối")


@pytest.mark.django_db
class TestIsVocabularyEligibleForSrs:

    def test_UT_PRG_SM2_001_new_vocab_without_mastery_is_eligible(self, user, vocab):
        """UT-PRG-SM2-001: Từ mới chưa có mastery → eligible = True."""
        assert SM2Service.is_vocabulary_eligible_for_srs(user, vocab) is True

    def test_vocab_with_null_next_review_is_eligible(self, user, vocab):
        """Mastery có next_review_date=None (từ mới học) → eligible = True."""
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=None
        )
        assert SM2Service.is_vocabulary_eligible_for_srs(user, vocab) is True

    def test_vocab_not_yet_due_is_not_eligible(self, user, vocab):
        """Mastery có next_review_date trong tương lai → not eligible."""
        future = timezone.now() + timedelta(days=5)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=future
        )
        assert SM2Service.is_vocabulary_eligible_for_srs(user, vocab) is False


@pytest.mark.django_db
class TestUpdateReview:

    def test_UT_PRG_SM2_002_update_review_returns_none_when_not_due(self, user, vocab):
        """UT-PRG-SM2-002: update_review trả None khi chưa đến hạn và không force."""
        future = timezone.now() + timedelta(days=3)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, next_review_date=future
        )
        result = SM2Service.update_review(user, vocab, is_correct=True, force_update=False)
        assert result is None

    def test_UT_PRG_SM2_003_correct_answer_increases_repetitions_and_interval(self, user, vocab):
        """UT-PRG-SM2-003: Trả lời đúng → repetitions tăng, interval tăng (else branch), EF >= 1.3."""
        past = timezone.now() - timedelta(days=1)
        # repetitions=2 → vào nhánh else: interval = int(interval * ease_factor)
        UserVocabularyMastery.objects.create(
            user=user,
            vocabulary=vocab,
            repetitions=2,
            interval=6,
            ease_factor=2.5,
            next_review_date=past,
        )
        result = SM2Service.update_review(user, vocab, is_correct=True)
        assert result is not None
        assert result.repetitions == 3
        assert result.interval == int(6 * 2.5)
        assert result.ease_factor >= 1.3

    def test_UT_PRG_SM2_004_wrong_answer_resets_repetitions_and_interval(self, user, vocab):
        """UT-PRG-SM2-004: Trả lời sai → repetitions=0, interval=1."""
        past = timezone.now() - timedelta(days=1)
        UserVocabularyMastery.objects.create(
            user=user,
            vocabulary=vocab,
            repetitions=5,
            interval=30,
            ease_factor=2.5,
            next_review_date=past,
        )
        result = SM2Service.update_review(user, vocab, is_correct=False)
        assert result is not None
        assert result.repetitions == 0
        assert result.interval == 1

    def test_ease_factor_clamped_at_1_3(self, user, vocab):
        """EF không được thấp hơn 1.3 dù trả lời sai nhiều lần."""
        past = timezone.now() - timedelta(days=1)
        UserVocabularyMastery.objects.create(
            user=user, vocabulary=vocab, ease_factor=1.31, next_review_date=past
        )
        result = SM2Service.update_review(user, vocab, is_correct=False)
        assert result.ease_factor >= 1.3


@pytest.mark.django_db
class TestGetVocabulariesDueForReview:

    def test_UT_PRG_SM2_005_returns_only_due_vocabularies_in_order(self, user, vocab, vocab2):
        """UT-PRG-SM2-005: Chỉ trả mastery đến hạn, đúng thứ tự next_review_date."""
        now = timezone.now()
        past1 = now - timedelta(days=2)
        past2 = now - timedelta(days=1)
        future = now + timedelta(days=5)

        UserVocabularyMastery.objects.create(user=user, vocabulary=vocab, next_review_date=past1)
        UserVocabularyMastery.objects.create(user=user, vocabulary=vocab2, next_review_date=future)

        # Create a third vocab to test the ordering
        course = Course.objects.get_or_create(title="Test Course")[0]
        topic = Topic.objects.get_or_create(course=course, title="Test Topic")[0]
        vocab3 = Vocabulary.objects.create(topic=topic, word="cherry", meaning="quả anh đào")
        UserVocabularyMastery.objects.create(user=user, vocabulary=vocab3, next_review_date=past2)

        due = SM2Service.get_vocabularies_due_for_review(user)
        due_vocab_ids = [m.vocabulary_id for m in due]

        assert vocab.id in due_vocab_ids
        assert vocab3.id in due_vocab_ids
        assert vocab2.id not in due_vocab_ids
        # Verify order: oldest due first
        assert due[0].vocabulary_id == vocab.id
        assert due[1].vocabulary_id == vocab3.id
