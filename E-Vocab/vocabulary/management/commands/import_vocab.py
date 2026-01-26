import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from vocabulary.models import Course, Topic, Vocabulary

class Command(BaseCommand):
    help = 'Import topics and words for a specific course from a CSV file'

    def handle(self, *args, **kwargs):
        # 1. Tên khóa học chính mà file này thuộc về
        course_title = "Toeic 600 từ"
        
        # 2. Tên file CSV trong thư mục /data/
        file_name = 'toeic_600tuvung.csv'
        
        # Tự động tạo hoặc lấy khóa học chính
        course, created = Course.objects.get_or_create(title=course_title)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created main course: "{course.title}"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing main course: "{course.title}"'))
        
        csv_file_path = os.path.join(settings.BASE_DIR, 'data', file_name)

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None) # Bỏ qua dòng tiêu đề

                word_count = 0
                for row in reader:
                    # Ánh xạ các cột trong CSV của bạn
                    # row[0] -> Tên Chủ đề / Bài học (ví dụ: "Contracts")
                    # row[1] -> Từ vựng (ví dụ: "Abide by")
                    # row[2] -> Nghĩa của từ
                    # row[3] -> Câu ví dụ
                    topic_title = row[0]
                    word_text = row[1]
                    meaning_text = row[2]
                    example_text = row[3] if len(row) > 3 else ""

                    # Lấy hoặc tạo "Topic" (bài học) và liên kết với khóa học chính
                    topic, _ = Topic.objects.get_or_create(
                        course=course,
                        title=topic_title
                    )

                    # Tạo từ vựng và liên kết với Topic tương ứng
                    # Dùng get_or_create để tránh tạo trùng từ vựng nếu chạy lại script
                    Vocabulary.objects.get_or_create(
                        topic=topic,
                        word=word_text,
                        defaults={
                            'meaning': meaning_text,
                            'example': example_text
                        }
                    )
                    word_count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully processed {word_count} words!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at: {csv_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))