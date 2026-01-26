from rest_framework import serializers
from .models import LearningSession, Question, UserAnswer
from vocabulary.serializers import VocabularySerializer


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer cho Question."""
    
    vocabulary = VocabularySerializer(read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'vocabulary', 'question_type', 'order', 'content', 'correct_answer', 'explanation']
        read_only_fields = ['id']


class UserAnswerSerializer(serializers.ModelSerializer):
    """Serializer cho UserAnswer."""
    
    class Meta:
        model = UserAnswer
        fields = ['id', 'session', 'question', 'selected_option', 'answer_text', 'is_correct', 'time_spent', 'answered_at']
        read_only_fields = ['id', 'answered_at']


class LearningSessionSerializer(serializers.ModelSerializer):
    """Serializer cho LearningSession."""
    
    questions = QuestionSerializer(many=True, read_only=True)
    user_answers = UserAnswerSerializer(many=True, read_only=True)
    topic = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningSession
        fields = [
            'id', 'user', 'topic', 'mode', 'time_limit', 'total_questions', 
            'pass_score', 'started_at', 'completed_at', 'score', 'is_passed',
            'questions', 'user_answers'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'completed_at', 'score', 'is_passed']
    
    def get_topic(self, obj):
        if obj.topic:
            return {
                'id': obj.topic.id,
                'title': obj.topic.title
            }
        return None

