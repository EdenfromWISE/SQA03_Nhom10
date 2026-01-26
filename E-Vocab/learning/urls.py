from django.urls import path
from . import views

urlpatterns = [
    # Tạo session
    path("sessions/practice/", views.create_practice_session, name="create_practice_session"),
    path("sessions/review/", views.create_review_session, name="create_review_session"),
    path("sessions/exam/", views.create_exam_session, name="create_exam_session"),
    
    # Làm việc với session
    path("sessions/<int:session_id>/", views.get_session, name="get_session"),
    path("sessions/<int:session_id>/detail/", views.get_session_detail, name="get_session_detail"),
    path("sessions/<int:session_id>/questions/", views.get_questions, name="get_questions"),
    path("sessions/<int:session_id>/submit-answer/", views.submit_answer, name="submit_answer"),
    path("sessions/<int:session_id>/complete/", views.complete_session, name="complete_session"),
    path("sessions/<int:session_id>/cancel/", views.cancel_session, name="cancel_session"),
    
    # Lịch sử
    path("sessions/history/", views.get_session_history, name="get_session_history"),
    
    # Đánh giá phát âm
    path("pronunciation/assess/", views.assess_pronunciation, name="assess_pronunciation"),
]