"""
Unit tests for vocabulary/models.py
Covers: __str__ của Course, Topic, Vocabulary
"""
import pytest
from vocabulary.models import Course, Topic, Vocabulary


@pytest.mark.django_db
class TestCourseModel:

    def test_UT_VOC_MOD_001_course_str(self):
        """UT-VOC-MOD-001: Course.__str__ trả về title."""
        course = Course.objects.create(title="English Basics")
        assert str(course) == "English Basics"


@pytest.mark.django_db
class TestTopicModel:

    def test_UT_VOC_MOD_001_topic_str(self):
        """UT-VOC-MOD-001: Topic.__str__ trả về '{course.title} - {topic.title}'."""
        course = Course.objects.create(title="English Basics")
        topic = Topic.objects.create(course=course, title="Animals")
        assert str(topic) == "English Basics - Animals"


@pytest.mark.django_db
class TestVocabularyModel:

    def test_UT_VOC_MOD_001_vocabulary_str(self):
        """UT-VOC-MOD-001: Vocabulary.__str__ trả về word."""
        course = Course.objects.create(title="English Basics")
        topic = Topic.objects.create(course=course, title="Animals")
        vocab = Vocabulary.objects.create(topic=topic, word="cat", meaning="con mèo")
        assert str(vocab) == "cat"
