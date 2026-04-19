"""
progress/tests/test_views.py
Unit tests cho progress/views.py

Test Cases:
    UT-PRG-VIEW-001 — UpcomingReviewAPIView: từ quá hạn được nhóm vào ngày hôm nay
    UT-PRG-VIEW-002 — OverviewAPIView: trả đủ 4 chỉ số
    UT-PRG-VIEW-003 — DailyProgressAPIView: luôn trả 7 mục T2..CN
    UT-PRG-VIEW-004 — RecentSessionsAPIView: mỗi session item đúng key contract

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from learning.models import LearningSession
from progress.models import UserVocabularyMastery, UserStreak
from vocabulary.models import Course, Topic, Vocabulary

UPCOMING_URL       = "/api/progress/upcoming-review/"
OVERVIEW_URL       = "/api/progress/overview/"
DAILY_PROGRESS_URL = "/api/progress/daily-progress/"
RECENT_SESSIONS_URL = "/api/progress/recent-sessions/"
STREAK_URL         = "/api/progress/streak/"


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def vocab_pair(db):
    """2 từ vựng trong cùng topic — dùng cho các test cần mastery hoặc session."""
    course = Course.objects.create(title="PV Course")
    topic  = Topic.objects.create(course=course, title="PV Topic")
    v1 = Vocabulary.objects.create(topic=topic, word="alpha", meaning="m1")
    v2 = Vocabulary.objects.create(topic=topic, word="beta",  meaning="m2")
    return topic, v1, v2


@pytest.fixture
def force_client(user):
    """
    APIClient dùng force_authenticate để bỏ qua JWT.
    Dùng cho các view không khai báo permission_classes tường minh.
    """
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ══════════════════════════════════════════════════════════════════════════════
# UpcomingReviewAPIView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestUpcomingReviewAPIView:

    # ── UT-PRG-VIEW-001 ────────────────────────────────────────────────────
    def test_UT_PRG_VIEW_001_overdue_words_grouped_under_today(
        self, force_client, user, vocab_pair
    ):
        # TC: UT-PRG-VIEW-001 — Từ quá hạn (next_review_date trong quá khứ) được nhóm vào ngày hôm nay
        # [Arrange] Tạo mastery đã quá hạn 3 ngày
        _, v1, _ = vocab_pair
        past    = timezone.now() - timedelta(days=3)
        mastery = UserVocabularyMastery.objects.create(
            user=user, vocabulary=v1, next_review_date=past
        )
        # Bypass auto_now: dùng .update() để đặt last_practiced_at xa về quá khứ
        long_ago = timezone.now() - timedelta(days=30)
        UserVocabularyMastery.objects.filter(pk=mastery.pk).update(last_practiced_at=long_ago)

        # [CheckDB] Xác nhận mastery đã có next_review_date trong quá khứ
        assert UserVocabularyMastery.objects.filter(user=user).count() == 1

        # [Act]
        response = force_client.get(UPCOMING_URL)

        # [Assert] Trả list, entry đầu tiên (hôm nay) phải có count >= 1
        assert response.status_code == 200
        data = response.data
        assert isinstance(data, list)
        assert len(data) >= 1
        today_entry = data[0]
        assert today_entry["count"] >= 1, "Từ quá hạn phải được nhóm vào ngày hôm nay"
        # [Rollback] UserVocabularyMastery sẽ bị rollback sau test

    def test_upcoming_review_empty_when_no_mastery(self, force_client):
        # [CheckDB] Xác nhận không có mastery trong DB
        # [Act]
        response = force_client.get(UPCOMING_URL)

        # [Assert] Tất cả ngày phải có count = 0
        assert response.status_code == 200
        for item in response.data:
            assert item["count"] == 0


# ══════════════════════════════════════════════════════════════════════════════
# OverviewAPIView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestOverviewAPIView:

    # ── UT-PRG-VIEW-002 ────────────────────────────────────────────────────
    def test_UT_PRG_VIEW_002_overview_returns_four_required_keys(self, force_client):
        # TC: UT-PRG-VIEW-002 — OverviewAPIView trả đủ 4 chỉ số theo contract
        # [Act]
        response = force_client.get(OVERVIEW_URL)

        # [Assert] Bốn field bắt buộc phải có trong response
        assert response.status_code == 200
        for key in (
            "total_learned_count",
            "new_words_today",
            "overdue_and_due_today_not_reviewed",
            "due_today_and_reviewed",
        ):
            assert key in response.data, f"OverviewAPIView thiếu field: {key}"

    def test_overview_total_learned_count_reflects_mastery_objects(
        self, force_client, user, vocab_pair
    ):
        # [Arrange] Tạo 2 mastery cho user
        _, v1, v2 = vocab_pair
        UserVocabularyMastery.objects.create(user=user, vocabulary=v1)
        UserVocabularyMastery.objects.create(user=user, vocabulary=v2)

        # [CheckDB] Xác nhận 2 mastery trong DB
        assert UserVocabularyMastery.objects.filter(user=user).count() == 2

        # [Act]
        response = force_client.get(OVERVIEW_URL)

        # [Assert] total_learned_count phải bằng số mastery
        assert response.data["total_learned_count"] == 2
        # [Rollback] UserVocabularyMastery sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# DailyProgressAPIView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestDailyProgressAPIView:

    # ── UT-PRG-VIEW-003 ────────────────────────────────────────────────────
    def test_UT_PRG_VIEW_003_daily_progress_returns_7_items_with_correct_labels(
        self, force_client
    ):
        # TC: UT-PRG-VIEW-003 — DailyProgressAPIView luôn trả 7 mục T2 → CN
        # [Act]
        response = force_client.get(DAILY_PROGRESS_URL)

        # [Assert] Đúng 7 ngày, nhãn đúng thứ tự T2..CN
        assert response.status_code == 200
        data   = response.data
        assert len(data) == 7, "Daily progress phải có đúng 7 ngày"
        labels = [item["day"] for item in data]
        assert labels == ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    def test_daily_progress_words_field_is_non_negative(self, force_client):
        # [Act]
        response = force_client.get(DAILY_PROGRESS_URL)

        # [Assert] Số từ mỗi ngày không âm
        for item in response.data:
            assert item["words"] >= 0, f"words phải >= 0 nhưng nhận {item['words']}"


# ══════════════════════════════════════════════════════════════════════════════
# RecentSessionsAPIView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestRecentSessionsAPIView:

    # ── UT-PRG-VIEW-004 ────────────────────────────────────────────────────
    def test_UT_PRG_VIEW_004_recent_sessions_format_contract(
        self, force_client, user, vocab_pair
    ):
        # TC: UT-PRG-VIEW-004 — Mỗi session item có đúng các key theo contract
        # [Arrange] Tạo 1 completed session
        topic, _, _ = vocab_pair
        now = timezone.now()
        LearningSession.objects.create(
            user=user, topic=topic, mode="practice",
            time_limit=10, total_questions=5, pass_score=0,
            score=80.0, completed_at=now,
        )

        # [CheckDB] Xác nhận session đã được tạo trong DB
        assert LearningSession.objects.filter(user=user, completed_at__isnull=False).count() == 1

        # [Act]
        response = force_client.get(RECENT_SESSIONS_URL)

        # [Assert] Trả ít nhất 1 item, đủ các key contract
        assert response.status_code == 200
        assert len(response.data) >= 1
        item = response.data[0]
        for key in ("time", "type", "wordsCount", "result", "status", "learnedAt"):
            assert key in item, f"RecentSessionsAPIView thiếu key: {key}"
        # [Rollback] LearningSession sẽ bị rollback sau test

    def test_recent_sessions_only_returns_completed(self, force_client, user, vocab_pair):
        # [Arrange] Tạo session chưa completed (completed_at=None)
        topic, _, _ = vocab_pair
        LearningSession.objects.create(
            user=user, topic=topic, mode="practice",
            time_limit=10, total_questions=5, pass_score=0,
            completed_at=None,
        )

        # [CheckDB] Xác nhận session chưa completed
        assert LearningSession.objects.filter(user=user, completed_at__isnull=True).count() == 1

        # [Act & Assert] Không có session completed → trả list rỗng
        response = force_client.get(RECENT_SESSIONS_URL)
        assert response.status_code == 200
        assert len(response.data) == 0, "Session chưa completed không được trả"

    def test_recent_sessions_returns_at_most_limit(self, force_client, user, vocab_pair):
        # [Arrange] Tạo 10 completed sessions
        topic, _, _ = vocab_pair
        now = timezone.now()
        for _ in range(10):
            LearningSession.objects.create(
                user=user, topic=topic, mode="practice",
                time_limit=10, total_questions=5, pass_score=0,
                score=70.0, completed_at=now,
            )

        # [CheckDB] Xác nhận 10 sessions đã tạo
        assert LearningSession.objects.filter(user=user).count() == 10

        # [Act & Assert] Không vượt giới hạn (default 7)
        response = force_client.get(RECENT_SESSIONS_URL)
        assert len(response.data) <= 7, "Không được trả quá 7 sessions"
        # [Rollback] Tất cả LearningSession sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# StreakAPIView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestStreakAPIView:

    def test_UT_PRG_STK_streak_api_returns_streak_data(self, force_client):
        # TC: UT-PRG-VIEW-005 — StreakAPIView trả current_streak, longest_streak, calendar
        # [Act]
        response = force_client.get(STREAK_URL)

        # [Assert] 3 key bắt buộc của StreakSerializer
        assert response.status_code == 200
        for key in ("current_streak", "longest_streak", "calendar"):
            assert key in response.data, f"StreakAPIView thiếu key: {key}"

    def test_streak_api_calendar_has_correct_day_count(self, force_client):
        # [Arrange] Lấy số ngày đúng của tháng hiện tại để so sánh
        import calendar as cal_module
        from django.utils import timezone as tz
        now = tz.now()
        _, days_in_month = cal_module.monthrange(now.year, now.month)

        # [Act]
        response = force_client.get(STREAK_URL)

        # [Assert] calendar.days phải có đúng số ngày trong tháng
        assert len(response.data["calendar"]["days"]) == days_in_month, (
            f"calendar.days phải có {days_in_month} ngày cho tháng {now.month}/{now.year}"
        )
