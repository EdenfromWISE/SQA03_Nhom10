from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatMessage(models.Model):
    """Model để lưu lịch sử chat của người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ])
    content = models.TextField()
    timestamp = models.BigIntegerField()
    
    # Các trường bổ sung cho pronunciation messages
    message_type = models.CharField(max_length=50, null=True, blank=True)
    audio_url = models.CharField(max_length=500, null=True, blank=True)
    word = models.CharField(max_length=200, null=True, blank=True)
    phonetic = models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.content[:50]}"

