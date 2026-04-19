"""
Unit tests for vocabulary/views.py
Covers: CourseListView, CourseDetailView, TopicDetailView
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary

COURSES_URL = "/api/vocabulary/courses/"
TOPICS_URL = "/api/vocabulary/topics/"


@pytest.mark.django_db
class TestCourseListView:

    def test_UT_VOC_VIEW_001_anonymous_user_gets_401_or_403(self, api_client):
        """UT-VOC-VIEW-001: CourseListView yêu cầu authentication."""
        response = api_client.get(COURSES_URL)
        assert response.status_code in (401, 403)

    def test_authenticated_user_gets_200(self, auth_client):
        """Authenticated user có thể truy cập CourseListView."""
        response = auth_client.get(COURSES_URL)
        assert response.status_code == 200


@pytest.mark.django_db
class TestCourseDetailView:

    def test_UT_VOC_VIEW_002_course_detail_returns_correct_data(self, auth_client):
        """UT-VOC-VIEW-002: CourseDetailView trả đúng dữ liệu course."""
        course = Course.objects.create(title="English Basics", description="Basics")
        response = auth_client.get(f"{COURSES_URL}{course.pk}/")
        assert response.status_code == 200
        assert response.data["title"] == "English Basics"
        assert "topics" in response.data

    def test_course_detail_not_found_returns_404(self, auth_client):
        """CourseDetailView trả 404 khi pk không tồn tại."""
        response = auth_client.get(f"{COURSES_URL}99999/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestTopicDetailView:

    def test_UT_VOC_VIEW_003_topic_detail_returns_vocabulary_list(self, auth_client):
        """UT-VOC-VIEW-003: TopicDetailView trả đúng topic detail kèm vocabulary list."""
        course = Course.objects.create(title="English Basics")
        topic = Topic.objects.create(course=course, title="Animals")
        Vocabulary.objects.create(topic=topic, word="cat", meaning="con mèo")
        response = auth_client.get(f"{TOPICS_URL}{topic.pk}/")
        assert response.status_code == 200
        assert "vocabularies" in response.data
        assert len(response.data["vocabularies"]) == 1
        assert response.data["vocabularies"][0]["word"] == "cat"
