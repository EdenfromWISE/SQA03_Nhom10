from datetime import timedelta, datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict

from progress.models import UserStreak, UserVocabularyMastery
from progress.serializers import StreakSerializer
from progress.services.streak_service import StreakService
from learning.models import LearningSession

class StreakAPIView(APIView):

    def get(self, request):
        user = request.user

        # lấy streak
        streak, _ = UserStreak.objects.get_or_create(user=user)

        # lấy tháng param hoặc default = tháng hiện tại
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        today = timezone.now().date()
        year = int(year) if year else today.year
        month = int(month) if month else today.month

        calendar_data = StreakService.get_streak_calendar(
            user=user, year=year, month=month
        )

        data = {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "today": timezone.now().date().isoformat(),
            "calendar": calendar_data,
        }

        serializer = StreakSerializer(data)
        return Response(serializer.data)


class UpcomingReviewAPIView(APIView):
    """
    API để lấy danh sách từ vựng sắp ôn tập trong 7 ngày tới.
    Trả về dữ liệu được nhóm theo ngày.
    """

    def get(self, request):
        user = request.user
        
        # Lấy số ngày từ query param, mặc định là 7
        days = int(request.query_params.get("days", 7))
        
        # Tính toán khoảng thời gian - bắt đầu từ đầu ngày hôm nay
        now = timezone.now()
        local_now = timezone.localtime(now)
        today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        # Kết thúc vào cuối ngày thứ (days-1) - tức là bao gồm cả ngày thứ (days-1)
        end_date = today_start + timedelta(days=days)
        
        # Lấy tất cả từ vựng có next_review_date từ đầu ngày hôm nay đến hết ngày thứ (days-1)
        # Bao gồm cả các từ đã đến hạn (quá hạn) trong ngày hôm nay
        masteries_future = UserVocabularyMastery.objects.filter(
            user=user,
            next_review_date__isnull=False,
            next_review_date__gte=today_start,
            next_review_date__lt=end_date
        ).select_related('vocabulary').order_by('next_review_date')
        
        # Lấy các từ đã quá hạn (next_review_date < today_start) nhưng chưa được ôn tập
        # Điều kiện: next_review_date < today_start và (last_practiced_at < next_review_date hoặc last_practiced_at is None)
        overdue_masteries = UserVocabularyMastery.objects.filter(
            user=user,
            next_review_date__isnull=False,
            next_review_date__lt=today_start
        ).select_related('vocabulary')
        
        # Lọc các từ quá hạn chưa được ôn tập
        overdue_not_reviewed = []
        for mastery in overdue_masteries:
            if mastery.last_practiced_at is None or mastery.last_practiced_at < mastery.next_review_date:
                overdue_not_reviewed.append(mastery)
        
        # Nhóm theo ngày (chỉ lấy phần date, bỏ qua time)
        # Đảm bảo sử dụng local timezone để lấy date chính xác
        grouped_by_date = defaultdict(list)
        
        # Thêm các từ quá hạn vào ngày hôm nay
        today_date_string = local_now.date().isoformat()
        for mastery in overdue_not_reviewed:
            grouped_by_date[today_date_string].append({
                "word": mastery.vocabulary.word
            })
        
        # Thêm các từ sắp đến hạn
        for mastery in masteries_future:
            # Chuyển next_review_date về local timezone trước khi lấy date
            # Đảm bảo date được lấy đúng theo timezone hiện tại
            if timezone.is_aware(mastery.next_review_date):
                # Nếu là timezone-aware, chuyển về local timezone
                local_review_date = timezone.localtime(mastery.next_review_date)
                review_date = local_review_date.date()
            else:
                # Nếu là naive datetime, lấy date trực tiếp
                review_date = mastery.next_review_date.date()
            date_string = review_date.isoformat()
            grouped_by_date[date_string].append({
                "word": mastery.vocabulary.word
            })
        
        # Chuyển đổi thành format mong muốn: mảng các object {date, count, words}
        # Bắt đầu từ ngày hôm nay
        result = []
        current_date = local_now.date()
        for i in range(days):
            date = current_date + timedelta(days=i)
            date_string = date.isoformat()
            
            words = grouped_by_date.get(date_string, [])
            result.append({
                "date": date_string,
                "count": len(words),
                "words": words
            })
        
        return Response(result)


class OverviewAPIView(APIView):
    """
    API để lấy tổng quan thống kê học tập của người dùng.
    Trả về:
    - Tổng số từ đã học từ trước đến nay
    - Số từ mới đã học trong ngày hôm nay
    - Số từ đến hạn ôn tập (hôm nay và trước) nhưng chưa ôn tập
    - Số từ đến hạn ôn tập hôm nay nhưng đã được ôn tập
    """

    def get(self, request):
        user = request.user
        now = timezone.now()
        
        # Lấy ngày hôm nay theo local timezone (Asia/Ho_Chi_Minh)
        # Đảm bảo tính đúng ngày hôm nay theo múi giờ địa phương
        local_now = timezone.localtime(now)
        today = local_now.date()
        
        # Lấy ngày hôm nay (start và end của ngày) theo local timezone
        # Tạo datetime với local timezone để so sánh chính xác
        today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = local_now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 1. Tổng số từ đã học từ trước đến nay (tổng số mastery của user)
        total_learned_count = UserVocabularyMastery.objects.filter(
            user=user
        ).count()
        
        # 2. Số từ mới đã học trong ngày hôm nay và số từ đã ôn tập
        # Phân biệt giữa từ mới học và từ ôn tập dựa vào tổng số lần luyện tập
        masteries_practiced_today = UserVocabularyMastery.objects.filter(
            user=user,
            last_practiced_at__gte=today_start,
            last_practiced_at__lte=today_end
        )
        
        new_words_today = 0
        reviewed_words_today = 0
        
        for mastery in masteries_practiced_today:
            total_attempts = mastery.correct_count + mastery.incorrect_count
            # Nếu chỉ mới làm 1 lần trong tổng số -> từ mới học hôm nay
            # (vì nếu đã học trước đó thì total_attempts sẽ > 1)
            if total_attempts == 1:
                new_words_today += 1
            else:
                # Nếu đã có nhiều hơn 1 lần luyện tập -> từ đã học trước đó, đây là ôn tập
                reviewed_words_today += 1
        
        # 3. Số từ đến hạn ôn tập (hôm nay và trước) nhưng chưa ôn tập
        # Điều kiện: next_review_date <= today_end và last_practiced_at < next_review_date
        # (tức là chưa được ôn tập sau khi đến hạn)
        all_due_today = UserVocabularyMastery.objects.filter(
            user=user,
            next_review_date__isnull=False,
            next_review_date__lte=today_end
        )
        
        overdue_and_due_today_not_reviewed_count = 0
        for mastery in all_due_today:
            # Nếu last_practiced_at < next_review_date thì chưa được ôn tập sau khi đến hạn
            if mastery.last_practiced_at is None or mastery.last_practiced_at < mastery.next_review_date:
                overdue_and_due_today_not_reviewed_count += 1
        
        # 4. Số từ đã ôn tập trong ngày hôm nay
        # Điều kiện: last_practiced_at trong ngày hôm nay VÀ đã có nhiều hơn 1 lần luyện tập
        # (tức là đã học trước đó và đang ôn tập lại)
        due_today_and_reviewed = reviewed_words_today
        
        return Response({
            "total_learned_count": total_learned_count,
            "new_words_today": new_words_today,
            "overdue_and_due_today_not_reviewed": overdue_and_due_today_not_reviewed_count,
            "due_today_and_reviewed": due_today_and_reviewed,
        })


class DailyProgressAPIView(APIView):
    """
    API để lấy dữ liệu tiến trình học tập hàng ngày trong 7 ngày gần nhất.
    Trả về số từ đã học mỗi ngày trong tuần (từ thứ 2 đến chủ nhật).
    Format: [{ day: "T2", words: 5 }, { day: "T3", words: 8 }, ...]
    """

    def get(self, request):
        user = request.user
        now = timezone.now()
        
        # Lấy 7 ngày gần nhất (từ 6 ngày trước đến hôm nay)
        # Tính từ đầu tuần (thứ 2) đến cuối tuần (chủ nhật)
        today = now.date()
        
        # Tìm thứ 2 của tuần hiện tại (hoặc thứ 2 tuần trước nếu hôm nay là chủ nhật)
        # weekday() trả về: 0=Monday, 1=Tuesday, ..., 6=Sunday
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        # Tạo danh sách 7 ngày từ thứ 2 đến chủ nhật
        week_dates = [monday + timedelta(days=i) for i in range(7)]
        
        # Tên các ngày trong tuần bằng tiếng Việt
        day_names = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        
        # Tính số từ học mỗi ngày dựa trên last_practiced_at
        result = []
        for i, date in enumerate(week_dates):
            day_start = timezone.make_aware(
                datetime.combine(date, datetime.min.time())
            )
            day_end = timezone.make_aware(
                datetime.combine(date, datetime.max.time())
            )
            
            # Đếm số từ có last_practiced_at trong ngày này
            words_count = UserVocabularyMastery.objects.filter(
                user=user,
                last_practiced_at__gte=day_start,
                last_practiced_at__lte=day_end
            ).count()
            
            result.append({
                "day": day_names[i],
                "words": words_count
            })
        
        return Response(result)


class RecentSessionsAPIView(APIView):
    """
    API để lấy danh sách 7 phiên học gần nhất của người dùng.
    Trả về format phù hợp với component RecentVocabulary.
    Format: [
        {
            time: "Hôm nay, 14:30",
            type: "Học từ vựng",
            wordsCount: 15,
            result: "87%",
            status: "Hoàn thành",
            learnedAt: "Hôm nay"
        },
        ...
    ]
    """

    def get(self, request):
        user = request.user
        limit = int(request.query_params.get("limit", 7))
        
        # Lấy các phiên học đã hoàn thành, sắp xếp theo thời gian bắt đầu mới nhất
        sessions = LearningSession.objects.filter(
            user=user,
            completed_at__isnull=False
        ).order_by("-started_at")[:limit]
        
        now = timezone.now()
        result = []
        
        for session in sessions:
            # Format thời gian
            started_at_local = timezone.localtime(session.started_at) if timezone.is_aware(session.started_at) else session.started_at
            started_date = started_at_local.date()
            started_time = started_at_local.strftime("%H:%M")
            
            # Xác định "Hôm nay", "Hôm qua", hoặc số ngày trước
            today = now.date()
            if timezone.is_aware(now):
                today = timezone.localtime(now).date()
            
            days_diff = (today - started_date).days
            if days_diff == 0:
                time_str = f"Hôm nay, {started_time}"
                learned_at = "Hôm nay"
            elif days_diff == 1:
                time_str = f"Hôm qua, {started_time}"
                learned_at = "Hôm qua"
            else:
                time_str = f"{days_diff} ngày trước, {started_time}"
                learned_at = f"{days_diff} ngày trước"
            
            # Xác định loại phiên học
            if session.mode == "practice":
                session_type = "Học từ vựng"
            elif session.mode == "review":
                session_type = "Ôn tập"
            elif session.mode == "exam":
                session_type = "Kiểm tra"
            else:
                session_type = "Học từ vựng"
            
            # Số từ (số câu hỏi trong phiên)
            words_count = session.total_questions
            
            # Kết quả (điểm số dưới dạng phần trăm)
            # Score đã là phần trăm (0-100) rồi, không cần nhân với 100
            result_percent = int(session.score) if session.score is not None else 0
            result_str = f"{result_percent}%"
            
            # Trạng thái
            status = "Hoàn thành" if session.completed_at else "Đang học"
            
            result.append({
                "id": session.id,
                "time": time_str,
                "type": session_type,
                "wordsCount": words_count,
                "result": result_str,
                "status": status,
                "learnedAt": learned_at
            })
        
        return Response(result)