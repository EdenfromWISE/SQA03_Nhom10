from rest_framework import serializers
from .models import Course, Topic, Vocabulary

# ===================================================================
# Serializer cấp thấp nhất: chỉ cho một từ vựng
# ===================================================================
class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = (
            'id',
            'word',
            'meaning',
            'pronunciation',
            'audio_url',
            'image_url',
            'example_en',
            'example_vi',
        )


# ===================================================================
# Serializer cho Topic (Chủ đề/Bài học)
# ===================================================================

# Dùng để hiển thị trong danh sách (không kèm từ vựng)
class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'title', 'description', 'image_url')


# Dùng khi xem chi tiết một Topic (kèm theo tất cả từ vựng của nó)
class TopicDetailSerializer(serializers.ModelSerializer):
    vocabularies = VocabularySerializer(many=True, read_only=True)
    
    class Meta:
        model = Topic
        fields = ('id', 'title', 'description', 'vocabularies', 'image_url')


# ===================================================================
# Serializer cho Course (Khóa học chính)
# ===================================================================

# Dùng khi xem chi tiết một Course (kèm theo danh sách các Topic của nó)
class CourseSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'image_url', 'is_favorite', 'topics')
