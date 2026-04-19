"""
Unit tests for vocabulary/serializers.py
Covers: CourseSerializer, TopicDetailSerializer
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary
from vocabulary.serializers import CourseSerializer, TopicDetailSerializer


@pytest.mark.django_db
class TestCourseSerializer:

    def test_UT_VOC_SER_001_course_serializer_has_nested_topics(self):
        """UT-VOC-SER-001: CourseSerializer trả nested topics đúng fields."""
        course = Course.objects.create(title="My Course", description="Desc")
        topic = Topic.objects.create(course=course, title="Topic A")
        serializer = CourseSerializer(course)
        data = serializer.data
        assert "topics" in data
        assert len(data["topics"]) == 1
        assert data["topics"][0]["title"] == "Topic A"
        assert "id" in data["topics"][0]

    def test_course_serializer_fields(self):
        """CourseSerializer có đủ các fields cần thiết."""
        course = Course.objects.create(title="Test Course")
        data = CourseSerializer(course).data
        for field in ("id", "title", "description", "image_url", "is_favorite", "topics"):
            assert field in data


@pytest.mark.django_db
class TestTopicDetailSerializer:

    def test_UT_VOC_SER_002_topic_detail_serializer_has_nested_vocabularies(self):
        """UT-VOC-SER-002: TopicDetailSerializer trả nested vocabularies đúng field contract."""
        course = Course.objects.create(title="My Course")
        topic = Topic.objects.create(course=course, title="Animals")
        Vocabulary.objects.create(topic=topic, word="cat", meaning="con mèo")
        Vocabulary.objects.create(topic=topic, word="dog", meaning="con chó")
        serializer = TopicDetailSerializer(topic)
        data = serializer.data
        assert "vocabularies" in data
        assert len(data["vocabularies"]) == 2
        words = {v["word"] for v in data["vocabularies"]}
        assert words == {"cat", "dog"}

    def test_vocabulary_serializer_fields(self):
        """VocabularySerializer có đủ các fields cần thiết."""
        course = Course.objects.create(title="My Course")
        topic = Topic.objects.create(course=course, title="Animals")
        Vocabulary.objects.create(
            topic=topic,
            word="cat",
            meaning="con mèo",
            pronunciation="/kæt/",
        )
        data = TopicDetailSerializer(topic).data
        vocab_data = data["vocabularies"][0]
        for field in ("id", "word", "meaning", "pronunciation", "audio_url", "image_url"):
            assert field in vocab_data
