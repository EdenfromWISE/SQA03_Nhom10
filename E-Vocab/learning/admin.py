from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import LearningConfig, LearningSession, Question, UserAnswer


admin.site.register(LearningConfig, SingletonModelAdmin)


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    """Admin interface cho LearningSession."""
    
    list_display = ['id', 'user', 'topic', 'mode', 'score', 'is_passed', 'started_at', 'completed_at']
    list_filter = ['mode', 'is_passed', 'started_at', 'completed_at']
    search_fields = ['user__username', 'topic__title']
    readonly_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface cho Question."""
    
    list_display = ['id', 'session', 'vocabulary', 'question_type', 'order']
    list_filter = ['question_type', 'session__mode']
    search_fields = ['vocabulary__word', 'session__user__username']
    ordering = ['session', 'order']


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """Admin interface cho UserAnswer."""
    
    list_display = ['id', 'session', 'question', 'is_correct', 'time_spent', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['session__user__username', 'question__vocabulary__word']
    readonly_fields = ['answered_at']
    ordering = ['-answered_at']