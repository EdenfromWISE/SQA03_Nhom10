from datetime import date, timedelta
from django.db import transaction
from django.utils import timezone
import calendar

from progress.models import DailyActivity, UserStreak


class StreakService:
    """
    Cập nhật streak mỗi khi user hoàn tất 1 session học.
    Logic:
    - Nếu hôm nay user chưa có activity → tạo mới
    - Tính streak dựa vào last_active_date
    - Update cả current streak & longest streak
    """

    @staticmethod
    @transaction.atomic
    def update_streak(user):
        today = timezone.now().date()

        # 1. Check hoặc tạo DailyActivity
        activity, created = DailyActivity.objects.get_or_create(
            user=user, date=today,
            defaults={
                "is_active": True,
            }
        )

        # 2. Update UserStreak
        streak, _ = UserStreak.objects.get_or_create(user=user)

        # Nếu chưa bao giờ hoạt động
        if streak.last_active_date is None:
            streak.current_streak = 1
            streak.longest_streak = 1
            streak.last_active_date = today
            streak.save()
            return streak

        # 3. Nếu đã active hôm nay → không tăng streak
        if streak.last_active_date == today:
            return streak

        # 4. Nếu active ngày hôm qua → +1 streak
        if streak.last_active_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            # 5. Nếu bỏ lỡ → reset streak hiện tại
            streak.current_streak = 1

        # 6. Update longest streak
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)

        streak.last_active_date = today
        streak.save()

        return streak
    
    @staticmethod
    def get_streak_calendar(user, year, month):
        # lấy số ngày trong tháng
        _, last_day = calendar.monthrange(year, month)

        # chuẩn bị list ngày trong tháng
        days = []
        start = date(year, month, 1)
        end = date(year, month, last_day)

        # lấy toàn bộ DailyActivity trong tháng
        activity_map = {
            d.date: d.is_active
            for d in DailyActivity.objects.filter(
                user=user, date__range=(start, end)
            )
        }

        # build calendar
        for day in range(1, last_day + 1):
            d = date(year, month, day)
            days.append({
                "date": d,
                "active": activity_map.get(d, False)
            })

        return {
            "year": year,
            "month": month,
            "days": days
        }
