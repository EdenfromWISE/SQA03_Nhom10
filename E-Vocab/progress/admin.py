from django.contrib import admin

from .models import UserCourseProgress, UserTopicProgress, UserVocabularyMastery


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    """Admin interface cho UserTopicProgress."""
    
    list_display = ['user', 'topic', 'is_passed', 'best_score', 'attempts', 'last_attempt_at']
    list_filter = ['is_passed', 'topic__course']
    search_fields = ['user__username', 'topic__title']
    readonly_fields = ['last_attempt_at']


@admin.register(UserVocabularyMastery)
class UserVocabularyMasteryAdmin(admin.ModelAdmin):
    """Admin interface cho UserVocabularyMastery."""
    
    list_display = ['user', 'vocabulary', 'correct_count', 'incorrect_count', 'proficiency', 'last_practiced_at']
    list_filter = ['vocabulary__topic']
    search_fields = ['user__username', 'vocabulary__word']
    readonly_fields = ['last_practiced_at']


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    """Admin interface cho UserCourseProgress."""
    
    list_display = ['user', 'course', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'course']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['completed_at']