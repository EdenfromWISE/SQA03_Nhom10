"""
vocabulary/tests/test_serializers.py
Unit tests cho vocabulary/serializers.py

Test Cases:
    UT-VOC-SER-001 — CourseSerializer có nested topics đúng fields
    UT-VOC-SER-002 — TopicDetailSerializer có nested vocabularies đúng fields

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary
from vocabulary.serializers import CourseSerializer, TopicDetailSerializer


# ══════════════════════════════════════════════════════════════════════════════
# CourseSerializer
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCourseSerializer:

    # ── UT-VOC-SER-001 ─────────────────────────────────────────────────────
    def test_UT_VOC_SER_001_course_serializer_has_nested_topics(self):
        # TC: UT-VOC-SER-001 — CourseSerializer trả nested topics với đúng field contract
        # [Arrange] Tạo course và 1 topic liên kết
        course = Course.objects.create(title="My Course", description="Desc")
        topic  = Topic.objects.create(course=course, title="Topic A")

        # [CheckDB] Xác nhận dữ liệu đã có trong DB trước khi serialize
        assert Topic.objects.filter(course=course).count() == 1

        # [Act]
        data = CourseSerializer(course).data

        # [Assert] topics phải là list lồng, có đúng title và id
        assert "topics" in data
        assert len(data["topics"]) == 1
        assert data["topics"][0]["title"] == "Topic A"
        assert "id" in data["topics"][0]
        # [Rollback] Course và Topic sẽ bị rollback sau test

    def test_course_serializer_exposes_all_required_fields(self):
        # [Arrange]
        course = Course.objects.create(title="Test Course")

        # [CheckDB] Xác nhận course tồn tại
        assert Course.objects.filter(pk=course.pk).exists()

        # [Act]
        data = CourseSerializer(course).data

        # [Assert] Kiểm tra toàn bộ field contract của CourseSerializer
        for field in ("id", "title", "description", "image_url", "is_favorite", "topics"):
            assert field in data, f"CourseSerializer thiếu field: {field}"


# ══════════════════════════════════════════════════════════════════════════════
# TopicDetailSerializer
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestTopicDetailSerializer:

    # ── UT-VOC-SER-002 ─────────────────────────────────────────────────────
    def test_UT_VOC_SER_002_topic_detail_serializer_has_nested_vocabularies(self):
        # TC: UT-VOC-SER-002 — TopicDetailSerializer trả nested vocabularies đúng field contract
        # [Arrange] Tạo topic và 2 từ vựng
        course = Course.objects.create(title="My Course")
        topic  = Topic.objects.create(course=course, title="Animals")
        Vocabulary.objects.create(topic=topic, word="cat", meaning="con mèo")
        Vocabulary.objects.create(topic=topic, word="dog", meaning="con chó")

        # [CheckDB] Xác nhận 2 vocabulary đã có trong DB
        assert Vocabulary.objects.filter(topic=topic).count() == 2

        # [Act]
        data = TopicDetailSerializer(topic).data

        # [Assert] vocabularies phải lồng 2 bản ghi đúng word
        assert "vocabularies" in data
        assert len(data["vocabularies"]) == 2
        words = {v["word"] for v in data["vocabularies"]}
        assert words == {"cat", "dog"}
        # [Rollback] Tất cả objects sẽ bị rollback sau test

    def test_vocabulary_serializer_exposes_all_required_fields(self):
        # [Arrange] Tạo vocabulary có đầy đủ fields
        course = Course.objects.create(title="My Course")
        topic  = Topic.objects.create(course=course, title="Animals")
        Vocabulary.objects.create(
            topic=topic, word="cat", meaning="con mèo", pronunciation="/kæt/"
        )

        # [CheckDB] Xác nhận vocabulary tồn tại
        assert Vocabulary.objects.filter(topic=topic, word="cat").exists()

        # [Act]
        data   = TopicDetailSerializer(topic).data
        vocab_data = data["vocabularies"][0]

        # [Assert] Kiểm tra field contract của VocabularySerializer
        for field in ("id", "word", "meaning", "pronunciation", "audio_url", "image_url"):
            assert field in vocab_data, f"VocabularySerializer thiếu field: {field}"
