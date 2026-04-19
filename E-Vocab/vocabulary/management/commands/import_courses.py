import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from vocabulary.models import Course

class Command(BaseCommand):
    help = 'Import courses from CSV file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'courses.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Không tìm thấy file: {file_path}'))
            return

        self.stdout.write('Đang bắt đầu import Courses...')
        
        count = 0
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                course_id = int(row.get('id', 0))
                title = row.get('title', '').strip()
                description = row.get('description', '').strip()
                
                course, created = Course.objects.update_or_create(
                    id=course_id,
                    defaults={
                        'title': title,
                        'description': description,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Tạo course: {title}'))
                else:
                    self.stdout.write(f'Cập nhật course: {title}')
                
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Hoàn tất import {count} courses!'))