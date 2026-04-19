"""
vocabulary/tests/test_models.py
Unit tests cho vocabulary/models.py

Test Cases:
    UT-VOC-MOD-001 — Course.__str__ trả về title
    UT-VOC-MOD-002 — Topic.__str__ trả về '{course} - {topic}'
    UT-VOC-MOD-003 — Vocabulary.__str__ trả về word

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary


# ══════════════════════════════════════════════════════════════════════════════
# Course model
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCourseModel:

    # ── UT-VOC-MOD-001 ─────────────────────────────────────────────────────
    def test_UT_VOC_MOD_001_course_str_returns_title(self):
        # TC: UT-VOC-MOD-001 — Course.__str__ trả về title của course
        # [Arrange] Tạo course với title xác định
        course = Course.objects.create(title="English Basics")

        # [CheckDB] Xác nhận course đã được lưu vào DB
        assert Course.objects.filter(title="English Basics").exists()

        # [Act & Assert] __str__ phải khớp title
        assert str(course) == "English Basics"
        # [Rollback] Course sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# Topic model
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestTopicModel:

    # ── UT-VOC-MOD-002 ─────────────────────────────────────────────────────
    def test_UT_VOC_MOD_002_topic_str_returns_course_dash_title(self):
        # TC: UT-VOC-MOD-002 — Topic.__str__ trả '{course.title} - {topic.title}'
        # [Arrange] Tạo course và topic liên kết
        course = Course.objects.create(title="English Basics")
        topic  = Topic.objects.create(course=course, title="Animals")

        # [CheckDB] Xác nhận topic đã được lưu và liên kết đúng course
        assert Topic.objects.filter(course=course, title="Animals").exists()

        # [Act & Assert]
        assert str(topic) == "English Basics - Animals"
        # [Rollback] Course và Topic sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# Vocabulary model
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestVocabularyModel:

    # ── UT-VOC-MOD-003 ─────────────────────────────────────────────────────
    def test_UT_VOC_MOD_003_vocabulary_str_returns_word(self):
        # TC: UT-VOC-MOD-003 — Vocabulary.__str__ trả về word của từ vựng
        # [Arrange] Tạo đủ chuỗi Course → Topic → Vocabulary
        course = Course.objects.create(title="English Basics")
        topic  = Topic.objects.create(course=course, title="Animals")
        vocab  = Vocabulary.objects.create(topic=topic, word="cat", meaning="con mèo")

        # [CheckDB] Xác nhận vocabulary đã được tạo trong DB với đúng word
        assert Vocabulary.objects.filter(topic=topic, word="cat").exists()

        # [Act & Assert] __str__ phải là word, không phải meaning
        assert str(vocab) == "cat"
        # [Rollback] Course, Topic, Vocabulary sẽ bị rollback sau test
