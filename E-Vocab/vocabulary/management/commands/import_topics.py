import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from vocabulary.models import Topic, Course

class Command(BaseCommand):
    help = 'Import topics from CSV file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'topics.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Không tìm thấy file: {file_path}'))
            return

        self.stdout.write('Đang bắt đầu import Topics...')
        
        count = 0
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                topic_id = int(row.get('id', 0))
                title = row.get('title', '').strip()
                description = row.get('description', '').strip()
                image_url = row.get('image_url', '').strip()
                course_id = int(row.get('course', 0))
                
                try:
                    course = Course.objects.get(id=course_id)
                except Course.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Không tìm thấy course ID {course_id} cho topic {title}'))
                    continue
                
                topic, created = Topic.objects.update_or_create(
                    id=topic_id,
                    defaults={
                        'title': title,
                        'description': description,
                        'image_url': image_url,
                        'course': course,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Tạo topic: {title}'))
                else:
                    self.stdout.write(f'Cập nhật topic: {title}')
                
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Hoàn tất import {count} topics!'))