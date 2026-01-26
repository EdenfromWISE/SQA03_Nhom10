from django.db import models
from solo.models import SingletonModel

from django.contrib.auth.models import User
from vocabulary.models import Topic, Vocabulary

class LearningConfig(SingletonModel):
    """Cấu hình chung."""
    
    time_limit = models.IntegerField(default=10)
    total_questions = models.IntegerField(default=20)
    pass_score = models.IntegerField(default=80)
    max_daily_exams_per_topic = models.IntegerField(default=1)

    def __str__(self):
        return "Learning Configuration"


class LearningSession(models.Model):
    """Lưu trữ thông tin về một phiên học tập của người dùng."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.CASCADE)
    mode = models.CharField(max_length=20, choices=[('practice', 'Practice'), ('review', 'Review'), ('exam', 'Exam')])

    time_limit = models.IntegerField()
    total_questions = models.IntegerField()
    pass_score = models.IntegerField()

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
    
    def title(self):
        if self.mode == 'practice':
            return f"Practice Session of {self.topic.title}"
        elif self.mode == 'review':
            return f"Review Session"
        elif self.mode == 'exam':
            return f"Exam Session of {self.topic.title}"
        return f"Unknown Session of {self.topic.title}"


class Question(models.Model):
    """Lưu trữ thông tin về câu hỏi trong phiên học tập."""

    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='questions')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.SET_NULL, null=True, blank=True)
    question_type = models.CharField(max_length=50)
    order = models.IntegerField()

    content = models.JSONField()
    correct_answer = models.JSONField()
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order} in Session {self.session.id}"


class UserAnswer(models.Model):
    """Lưu trữ thông tin về câu trả lời của người dùng cho một câu hỏi."""

    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_option = models.CharField(max_length=50, null=True, blank=True)
    answer_text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    time_spent = models.FloatField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)