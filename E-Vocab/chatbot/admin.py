from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'content_preview', 'timestamp', 'created_at']
    list_filter = ['role', 'message_type', 'created_at']
    search_fields = ['content', 'user__username', 'word']
    readonly_fields = ['created_at']
    ordering = ['-timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

