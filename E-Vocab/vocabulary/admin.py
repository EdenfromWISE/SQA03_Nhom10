from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Course, Topic, Vocabulary

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = ('title', 'description')
    inlines = [TopicInline]

@admin.register(Topic)
class TopicAdmin(ImportExportModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)

@admin.register(Vocabulary)
class VocabularyAdmin(ImportExportModelAdmin):
    list_display = ('word', 'meaning', 'topic')
    list_filter = ('topic__course', 'topic')
    search_fields = ('word', 'meaning')
