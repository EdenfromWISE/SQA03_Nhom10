"""
Unit tests for progress/views.py
Covers: UpcomingReviewAPIView, OverviewAPIView, DailyProgressAPIView,
        RecentSessionsAPIView, StreakAPIView
"""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from learning.models import LearningSession
from progress.models import UserVocabularyMastery, UserStreak
from vocabulary.models import Course, Topic, Vocabulary

UPCOMING_URL = "/api/progress/upcoming-review/"
OVERVIEW_URL = "/api/progress/overview/"
DAILY_PROGRESS_URL = "/api/progress/daily-progress/"
RECENT_SESSIONS_URL = "/api/progress/recent-sessions/"
STREAK_URL = "/api/progress/streak/"


@pytest.fixture
def vocab_pair(db):
    course = Course.objects.create(title="PV Course")
    topic = Topic.objects.create(course=course, title="PV Topic")
    v1 = Vocabulary.objects.create(topic=topic, word="alpha", meaning="m1")
    v2 = Vocabulary.objects.create(topic=topic, word="beta", meaning="m2")
    return topic, v1, v2


@pytest.fixture
def force_client(user):
    """APIClient dùng force_authenticate để bỏ qua JWT, test view logic trực tiếp."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ─────────────────────────────────────────────────────────
# UpcomingReviewAPIView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUpcomingReviewAPIView:

    def test_UT_PRG_VIEW_001_overdue_words_grouped_under_today(
        self, force_client, user, vocab_pair
    ):
        """UT-PRG-VIEW-001: Từ quá hạn được nhóm vào ngày hôm nay."""
        _, v1, _ = vocab_pair
        past = timezone.now() - timedelta(days=3)
        mastery = UserVocabularyMastery.objects.create(
            user=user, vocabulary=v1, next_review_date=past
        )
        # Bypass auto_now: set last_practiced_at xa về quá khứ để pass điều kiện overdue
        long_ago = timezone.now() - timedelta(days=30)
        UserVocabularyMastery.objects.filter(pk=mastery.pk).update(last_practiced_at=long_ago)

        response = force_client.get(UPCOMING_URL)
        assert response.status_code == 200
        data = response.data
        assert isinstance(data, list)
        assert len(data) >= 1
        today_entry = data[0]
        assert today_entry["count"] >= 1

    def test_upcoming_review_empty_when_no_mastery(self, force_client):
        """Không có mastery → tất cả count = 0."""
        response = force_client.get(UPCOMING_URL)
        assert response.status_code == 200
        for item in response.data:
            assert item["count"] == 0


# ─────────────────────────────────────────────────────────
# OverviewAPIView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestOverviewAPIView:

    def test_UT_PRG_VIEW_002_overview_returns_four_required_keys(self, force_client):
        """UT-PRG-VIEW-002: OverviewAPIView trả đủ 4 chỉ số."""
        response = force_client.get(OVERVIEW_URL)
        assert response.status_code == 200
        for key in (
            "total_learned_count",
            "new_words_today",
            "overdue_and_due_today_not_reviewed",
            "due_today_and_reviewed",
        ):
            assert key in response.data, f"Missing key: {key}"

    def test_overview_total_learned_count_reflects_mastery_objects(
        self, force_client, user, vocab_pair
    ):
        """total_learned_count đúng với số UserVocabularyMastery của user."""
        _, v1, v2 = vocab_pair
        UserVocabularyMastery.objects.create(user=user, vocabulary=v1)
        UserVocabularyMastery.objects.create(user=user, vocabulary=v2)
        response = force_client.get(OVERVIEW_URL)
        assert response.data["total_learned_count"] == 2


# ─────────────────────────────────────────────────────────
# DailyProgressAPIView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestDailyProgressAPIView:

    def test_UT_PRG_VIEW_003_daily_progress_returns_7_items_with_correct_labels(
        self, force_client
    ):
        """UT-PRG-VIEW-003: DailyProgressAPIView luôn trả 7 mục T2..CN."""
        response = force_client.get(DAILY_PROGRESS_URL)
        assert response.status_code == 200
        data = response.data
        assert len(data) == 7
        labels = [item["day"] for item in data]
        assert labels == ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    def test_daily_progress_words_field_is_non_negative(self, force_client):
        """words field của mỗi ngày >= 0."""
        response = force_client.get(DAILY_PROGRESS_URL)
        for item in response.data:
            assert item["words"] >= 0


# ─────────────────────────────────────────────────────────
# RecentSessionsAPIView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRecentSessionsAPIView:

    def test_UT_PRG_VIEW_004_recent_sessions_format_contract(
        self, force_client, user, vocab_pair
    ):
        """UT-PRG-VIEW-004: Mỗi session item có đúng các key theo contract."""
        topic, _, _ = vocab_pair
        now = timezone.now()
        LearningSession.objects.create(
            user=user,
            topic=topic,
            mode="practice",
            time_limit=10,
            total_questions=5,
            pass_score=0,
            score=80.0,
            completed_at=now,
        )
        response = force_client.get(RECENT_SESSIONS_URL)
        assert response.status_code == 200
        assert len(response.data) >= 1
        item = response.data[0]
        for key in ("time", "type", "wordsCount", "result", "status", "learnedAt"):
            assert key in item, f"Missing key: {key}"

    def test_recent_sessions_only_returns_completed(self, force_client, user, vocab_pair):
        """Chỉ trả các session đã completed_at."""
        topic, _, _ = vocab_pair
        LearningSession.objects.create(
            user=user, topic=topic, mode="practice",
            time_limit=10, total_questions=5, pass_score=0,
            completed_at=None,
        )
        response = force_client.get(RECENT_SESSIONS_URL)
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_recent_sessions_returns_at_most_limit(self, force_client, user, vocab_pair):
        """Không vượt quá limit mặc định 7."""
        topic, _, _ = vocab_pair
        now = timezone.now()
        for _ in range(10):
            LearningSession.objects.create(
                user=user, topic=topic, mode="practice",
                time_limit=10, total_questions=5, pass_score=0,
                score=70.0, completed_at=now,
            )
        response = force_client.get(RECENT_SESSIONS_URL)
        assert len(response.data) <= 7


# ─────────────────────────────────────────────────────────
# StreakAPIView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStreakAPIView:

    def test_UT_PRG_STK_streak_api_returns_streak_data(self, force_client):
        """StreakAPIView trả current_streak, longest_streak, calendar."""
        response = force_client.get(STREAK_URL)
        assert response.status_code == 200
        # StreakSerializer expose: current_streak, longest_streak, calendar
        for key in ("current_streak", "longest_streak", "calendar"):
            assert key in response.data, f"Missing key: {key}"

    def test_streak_api_calendar_has_correct_day_count(self, force_client):
        """calendar.days có đúng số ngày trong tháng hiện tại."""
        import calendar as cal_module
        from django.utils import timezone as tz
        now = tz.now()
        _, days_in_month = cal_module.monthrange(now.year, now.month)
        response = force_client.get(STREAK_URL)
        assert len(response.data["calendar"]["days"]) == days_in_month
