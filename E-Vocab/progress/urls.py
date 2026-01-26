from django.urls import path
from .views import StreakAPIView, UpcomingReviewAPIView, OverviewAPIView, DailyProgressAPIView, RecentSessionsAPIView

urlpatterns = [
    path("streak/", StreakAPIView.as_view(), name="streak"),
    path("upcoming-review/", UpcomingReviewAPIView.as_view(), name="upcoming-review"),
    path("overview/", OverviewAPIView.as_view(), name="overview"),
    path("daily-progress/", DailyProgressAPIView.as_view(), name="daily-progress"),
    path("recent-sessions/", RecentSessionsAPIView.as_view(), name="recent-sessions"),
]
