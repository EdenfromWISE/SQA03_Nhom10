from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from vocabulary.models import Course, Topic, Vocabulary

User = get_user_model()


class UserCourseProgress(models.Model):
    """Tiến độ học tập của người dùng theo course."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="course_progress"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "course"]
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    def check_completion(self):
        """Kiểm tra và cập nhật trạng thái hoàn thành course."""
        total_topics = self.course.topics.count()
        passed_topics = UserTopicProgress.objects.filter(
            user=self.user, topic__course=self.course, is_passed=True
        ).count()

        if total_topics > 0 and passed_topics == total_topics:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()


class UserTopicProgress(models.Model):
    """Tiến độ học tập của người dùng theo topic."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="topic_progress"
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_passed = models.BooleanField(default=False)
    best_score = models.FloatField(default=0)
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "topic"]
        ordering = ["-last_attempt_at"]

    def __str__(self):
        return f"{self.user.username} - {self.topic.title}"


class UserVocabularyMastery(models.Model):
    """Mức độ thành thạo từ vựng của người dùng với thuật toán SM-2."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vocab_mastery"
    )
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)

    # Các trường cho SM-2
    interval = models.IntegerField(default=1)  # Khoảng thời gian (ngày)
    ease_factor = models.FloatField(default=2.5)  # Hệ số dễ dàng
    repetitions = models.IntegerField(default=0)  # Số lần lặp lại
    quality = models.IntegerField(default=0)  # Chất lượng câu trả lời cuối (0-5)
    next_review_date = models.DateTimeField(null=True, blank=True)

    # Các trường bổ sung
    correct_count = models.IntegerField(default=0)
    incorrect_count = models.IntegerField(default=0)
    proficiency = models.FloatField(default=0.0)
    last_practiced_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "vocabulary"]
        ordering = ["-last_practiced_at"]

    def __str__(self):
        return f"{self.user.username} - {self.vocabulary.word}"

    def update_proficiency(self):
        """Cập nhật mức độ thành thạo."""
        total_attempts = self.correct_count + self.incorrect_count
        if total_attempts > 0:
            self.proficiency = (self.correct_count / total_attempts) * 100
        else:
            self.proficiency = 0
        self.save()


class DailyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)  # quan trọng để query theo range
    is_active = models.BooleanField(default=True)  # true = user học ngày đó
    new_words_count = models.PositiveIntegerField(default=0, blank=True, null=True)  # Số từ mới học trong ngày
    review_words_count = models.PositiveIntegerField(default=0, blank=True, null=True)  # Số từ đã ôn tập trong ngày

    # Optional: lưu data chuyên sâu (nếu cần heatmap chi tiết)
    # xp_earned = models.PositiveIntegerField(default=0)
    # session_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")


class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
