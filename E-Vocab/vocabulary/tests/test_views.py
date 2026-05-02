"""
vocabulary/tests/test_views.py
Unit tests cho vocabulary/views.py

Test Cases:
    UT-VOC-VIEW-001 — CourseListView: anonymous → 401/403
    UT-VOC-VIEW-002 — CourseListView: authenticated → 200
    UT-VOC-VIEW-003 — CourseDetailView: trả đúng dữ liệu course
    UT-VOC-VIEW-004 — CourseDetailView: pk không tồn tại → 404
    UT-VOC-VIEW-005 — TopicDetailView: trả topic kèm vocabulary list

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary

COURSES_URL = "/api/vocabulary/courses/"
TOPICS_URL  = "/api/vocabulary/topics/"


# ══════════════════════════════════════════════════════════════════════════════
# CourseListView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCourseListView:

    # ── UT-VOC-VIEW-001 ────────────────────────────────────────────────────
    def test_UT_VOC_VIEW_001_anonymous_user_gets_401_or_403(self, api_client):
        # TC: UT-VOC-VIEW-001 — Anonymous user không được truy cập CourseListView
        # [Arrange] Không có credentials trên api_client (anonymous)
        # [Act]
        response = api_client.get(COURSES_URL)

        # [Assert] Phải bị từ chối (Unauthorized hoặc Forbidden)
        assert response.status_code in (401, 403), (
            "CourseListView phải yêu cầu authentication"
        )

    # ── UT-VOC-VIEW-002 ────────────────────────────────────────────────────
    def test_UT_VOC_VIEW_002_authenticated_user_gets_200(self, auth_client):
        # TC: UT-VOC-VIEW-002 — User đã xác thực được phép GET CourseListView
        # [Act] User đã xác thực truy cập course list
        response = auth_client.get(COURSES_URL)

        # [Assert]
        assert response.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# CourseDetailView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCourseDetailView:

    # ── UT-VOC-VIEW-003 ────────────────────────────────────────────────────
    def test_UT_VOC_VIEW_003_course_detail_returns_correct_data(self, auth_client):
        # TC: UT-VOC-VIEW-003 — CourseDetailView trả đúng title và nested topics
        # [Arrange] Tạo course trong DB
        course = Course.objects.create(title="English Basics", description="Basics")

        # [CheckDB] Xác nhận course đã tồn tại trong DB
        assert Course.objects.filter(pk=course.pk).exists()

        # [Act]
        response = auth_client.get(f"{COURSES_URL}{course.pk}/")

        # [Assert] Trả đúng title và có field topics
        assert response.status_code == 200
        assert response.data["title"] == "English Basics"
        assert "topics" in response.data
        # [Rollback] Course sẽ bị rollback sau test

    # ── UT-VOC-VIEW-004 ────────────────────────────────────────────────────
    def test_UT_VOC_VIEW_004_course_detail_not_found_returns_404(self, auth_client):
        # TC: UT-VOC-VIEW-004 — CourseDetailView trả 404 khi pk không tồn tại
        # [Arrange] pk 99999 chắc chắn không tồn tại
        # [CheckDB] Xác nhận không có course với pk đó
        assert not Course.objects.filter(pk=99999).exists()

        # [Act & Assert]
        response = auth_client.get(f"{COURSES_URL}99999/")
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# TopicDetailView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestTopicDetailView:

    # ── UT-VOC-VIEW-005 ────────────────────────────────────────────────────
    def test_UT_VOC_VIEW_005_topic_detail_returns_vocabulary_list(self, auth_client):
        # TC: UT-VOC-VIEW-005 — TopicDetailView trả đúng topic detail kèm vocabulary list
        # [Arrange] Tạo course, topic và 1 vocabulary
        course = Course.objects.create(title="English Basics")
        topic  = Topic.objects.create(course=course, title="Animals")
        Vocabulary.objects.create(topic=topic, word="cat", meaning="con mèo")

        # [CheckDB] Xác nhận vocabulary đã có trong DB
        assert Vocabulary.objects.filter(topic=topic, word="cat").exists()

        # [Act]
        response = auth_client.get(f"{TOPICS_URL}{topic.pk}/")

        # [Assert] Phải có vocabularies list với 1 item, word đúng
        assert response.status_code == 200
        assert "vocabularies" in response.data
        assert len(response.data["vocabularies"]) == 1
        assert response.data["vocabularies"][0]["word"] == "cat"
        # [Rollback] Course, Topic, Vocabulary sẽ bị rollback sau test
