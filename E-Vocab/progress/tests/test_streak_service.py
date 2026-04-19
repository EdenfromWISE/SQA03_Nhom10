"""
Unit tests for progress/services/streak_service.py
Covers: StreakService.update_streak, StreakService.get_streak_calendar
"""
import calendar
from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from progress.models import UserStreak, DailyActivity
from progress.services.streak_service import StreakService

User = get_user_model()


@pytest.mark.django_db
class TestUpdateStreak:

    def test_UT_PRG_STK_001_first_activity_creates_streak_one(self, user):
        """UT-PRG-STK-001: Lần hoạt động đầu tiên → current=1, longest=1."""
        today = date.today()
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)
        assert streak.current_streak == 1
        assert streak.longest_streak == 1
        assert streak.last_active_date == today

    def test_UT_PRG_STK_002_same_day_does_not_increase_streak(self, user):
        """UT-PRG-STK-002: Cùng ngày không tăng streak."""
        today = date.today()
        UserStreak.objects.create(user=user, current_streak=3, longest_streak=5, last_active_date=today)
        DailyActivity.objects.create(user=user, date=today, is_active=True)
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)
        assert streak.current_streak == 3

    def test_UT_PRG_STK_003_consecutive_day_increments_streak(self, user):
        """UT-PRG-STK-003: Ngày liên tiếp → current +1, longest cập nhật."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        UserStreak.objects.create(user=user, current_streak=4, longest_streak=4, last_active_date=yesterday)
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)
        assert streak.current_streak == 5
        assert streak.longest_streak == 5

    def test_UT_PRG_STK_004_broken_streak_resets_current(self, user):
        """UT-PRG-STK-004: Đứt chuỗi → current=1, longest giữ max cũ."""
        today = date.today()
        two_days_ago = today - timedelta(days=2)
        UserStreak.objects.create(user=user, current_streak=7, longest_streak=10, last_active_date=two_days_ago)
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)
        assert streak.current_streak == 1
        assert streak.longest_streak == 10

    def test_UT_PRG_STK_005_get_streak_calendar_returns_correct_day_count(self, user):
        """UT-PRG-STK-005: get_streak_calendar trả đầy đủ ngày trong tháng."""
        year, month = 2024, 2
        result = StreakService.get_streak_calendar(user, year, month)
        expected_days = calendar.monthrange(year, month)[1]
        assert len(result["days"]) == expected_days
        assert result["year"] == year
        assert result["month"] == month

    def test_get_streak_calendar_marks_active_days(self, user):
        """Ngày có DailyActivity active=True được đánh dấu active trong calendar."""
        year, month = 2024, 3
        active_date = date(2024, 3, 15)
        DailyActivity.objects.create(user=user, date=active_date, is_active=True)
        result = StreakService.get_streak_calendar(user, year, month)
        day_map = {item["date"]: item["active"] for item in result["days"]}
        assert day_map[active_date] is True
        assert day_map[date(2024, 3, 1)] is False
