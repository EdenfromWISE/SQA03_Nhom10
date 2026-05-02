"""
progress/tests/test_streak_service.py
Unit tests cho progress/services/streak_service.py

Test Cases:
    UT-PRG-STK-001 — Lần hoạt động đầu tiên tạo streak = 1
    UT-PRG-STK-002 — Cùng ngày không tăng streak
    UT-PRG-STK-003 — Ngày liên tiếp tăng streak
    UT-PRG-STK-004 — Đứt chuỗi reset current streak
    UT-PRG-STK-005 — get_streak_calendar trả đúng số ngày trong tháng
    UT-PRG-STK-006 — get_streak_calendar đánh dấu đúng ngày active từ DailyActivity

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
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
    """Kiểm thử StreakService.update_streak — cập nhật chuỗi ngày học liên tiếp."""

    # ── UT-PRG-STK-001 ─────────────────────────────────────────────────────
    def test_UT_PRG_STK_001_first_activity_creates_streak_one(self, user):
        # TC: UT-PRG-STK-001 — Lần hoạt động đầu tiên → current=1, longest=1
        # [Arrange] User chưa có UserStreak nào trong DB
        today = date.today()
        assert not UserStreak.objects.filter(user=user).exists()

        # [Act] Mock timezone.now() để đảm bảo "hôm nay" nhất quán
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)

        # [Assert]
        assert streak.current_streak == 1
        assert streak.longest_streak == 1
        assert streak.last_active_date == today

        # [CheckDB] UserStreak phải được tạo trong DB
        db_streak = UserStreak.objects.get(user=user)
        assert db_streak.current_streak == 1
        assert db_streak.longest_streak == 1
        # [Rollback] UserStreak và DailyActivity sẽ bị rollback sau test

    # ── UT-PRG-STK-002 ─────────────────────────────────────────────────────
    def test_UT_PRG_STK_002_same_day_does_not_increase_streak(self, user):
        # TC: UT-PRG-STK-002 — Cùng ngày gọi update_streak 2 lần → streak không tăng
        # [Arrange] Tạo UserStreak đã active hôm nay với streak = 3
        today = date.today()
        UserStreak.objects.create(
            user=user,
            current_streak=3,
            longest_streak=5,
            last_active_date=today,   # đã active hôm nay
        )
        DailyActivity.objects.create(user=user, date=today, is_active=True)

        # [CheckDB] Xác nhận streak ban đầu = 3 trước khi gọi
        assert UserStreak.objects.get(user=user).current_streak == 3

        # [Act]
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)

        # [Assert] Streak giữ nguyên, không tăng
        assert streak.current_streak == 3

        # [CheckDB] Giá trị trong DB không đổi
        assert UserStreak.objects.get(user=user).current_streak == 3

    # ── UT-PRG-STK-003 ─────────────────────────────────────────────────────
    def test_UT_PRG_STK_003_consecutive_day_increments_streak(self, user):
        # TC: UT-PRG-STK-003 — Ngày liên tiếp → current_streak +1, longest cập nhật
        # [Arrange] last_active_date = hôm qua
        today     = date.today()
        yesterday = today - timedelta(days=1)
        UserStreak.objects.create(
            user=user,
            current_streak=4,
            longest_streak=4,
            last_active_date=yesterday,
        )

        # [CheckDB] Xác nhận trạng thái ban đầu
        initial = UserStreak.objects.get(user=user)
        assert initial.current_streak == 4
        assert initial.last_active_date == yesterday

        # [Act]
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)

        # [Assert] current +1 = 5, longest cập nhật lên 5
        assert streak.current_streak == 5
        assert streak.longest_streak == 5

        # [CheckDB] Giá trị mới phải được lưu vào DB
        db_streak = UserStreak.objects.get(user=user)
        assert db_streak.current_streak == 5
        assert db_streak.last_active_date == today

    # ── UT-PRG-STK-004 ─────────────────────────────────────────────────────
    def test_UT_PRG_STK_004_broken_streak_resets_current(self, user):
        # TC: UT-PRG-STK-004 — Đứt chuỗi (>1 ngày bỏ lỡ) → current=1, longest giữ max cũ
        # [Arrange] last_active_date = 2 ngày trước (bỏ lỡ hôm qua)
        today        = date.today()
        two_days_ago = today - timedelta(days=2)
        UserStreak.objects.create(
            user=user,
            current_streak=7,
            longest_streak=10,
            last_active_date=two_days_ago,
        )

        # [Act]
        with patch("progress.services.streak_service.timezone") as mock_tz:
            mock_tz.now.return_value.date.return_value = today
            streak = StreakService.update_streak(user)

        # [Assert] current reset về 1, longest giữ nguyên 10
        assert streak.current_streak == 1
        assert streak.longest_streak == 10

        # [CheckDB] Xác nhận DB được cập nhật đúng
        db_streak = UserStreak.objects.get(user=user)
        assert db_streak.current_streak == 1
        assert db_streak.longest_streak == 10  # longest KHÔNG bị reset


@pytest.mark.django_db
class TestGetStreakCalendar:
    """Kiểm thử StreakService.get_streak_calendar."""

    # ── UT-PRG-STK-005 ─────────────────────────────────────────────────────
    def test_UT_PRG_STK_005_returns_correct_day_count(self, user):
        # TC: UT-PRG-STK-005 — get_streak_calendar trả đủ số ngày trong tháng
        # [Arrange] Dùng tháng 2/2024 (năm nhuận → 29 ngày)
        year, month = 2024, 2
        expected_days = calendar.monthrange(year, month)[1]  # = 29

        # [Act]
        result = StreakService.get_streak_calendar(user, year, month)

        # [Assert] Cấu trúc trả về đúng
        assert result["year"] == year
        assert result["month"] == month
        assert len(result["days"]) == expected_days, (
            f"Tháng {month}/{year} phải có {expected_days} ngày"
        )

    # ── UT-PRG-STK-006 ─────────────────────────────────────────────────────
    def test_UT_PRG_STK_006_active_days_marked_correctly(self, user):
        # TC: UT-PRG-STK-006 — Ngày có DailyActivity (is_active=True) phải được đánh dấu đúng trong calendar
        # [Arrange] Tạo DailyActivity cho 15/3/2024
        active_date = date(2024, 3, 15)
        DailyActivity.objects.create(user=user, date=active_date, is_active=True)

        # [CheckDB] Xác nhận DailyActivity đã lưu
        assert DailyActivity.objects.filter(user=user, date=active_date).exists()

        # [Act]
        result = StreakService.get_streak_calendar(user, 2024, 3)

        # [Assert] Ngày 15 phải active=True, ngày khác active=False
        day_map = {item["date"]: item["active"] for item in result["days"]}
        assert day_map[active_date] is True
        assert day_map[date(2024, 3, 1)] is False
        # [Rollback] DailyActivity sẽ bị rollback sau test
