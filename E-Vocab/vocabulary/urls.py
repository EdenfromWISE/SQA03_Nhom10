# from django.urls import path
# # from .views import RegisterView, CourseListView, CourseDetailView
# from .views import CourseListView, CourseDetailView, TopicDetailView

# urlpatterns = [
#     # path('register/', RegisterView.as_view(), name='register'),
#     path('courses/', CourseListView.as_view(), name='course-list'),
#     path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
# ]

from django.urls import path
from .views import CourseListView, CourseDetailView, TopicDetailView

urlpatterns = [
    # Danh sách tất cả khóa học
    path('courses/', CourseListView.as_view(), name='course-list'),
    
    # Chi tiết một khóa học (bao gồm các chủ đề/bài học)
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    
    # Chi tiết một chủ đề/bài học (bao gồm các từ vựng)
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
]