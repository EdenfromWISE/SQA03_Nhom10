from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Topic(models.Model):
    course = models.ForeignKey(Course, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Vocabulary(models.Model):
    topic = models.ForeignKey(Topic, related_name='vocabularies', on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    meaning = models.CharField(max_length=255)
    word_type = models.CharField(max_length=50, null=True, blank=True)
    pronunciation = models.CharField(max_length=100, null=True, blank=True)
    audio_url = models.CharField(max_length=255, null=True, blank=True)
    example_en = models.TextField(null=True, blank=True)
    example_vi = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.word
