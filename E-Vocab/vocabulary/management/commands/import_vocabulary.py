import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from vocabulary.models import Vocabulary, Topic 

class Command(BaseCommand):
    help = 'Import vocabulary from CSV file (Fix lỗi BOM và Type)'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'vocabulary.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Không tìm thấy file: {file_path}'))
            return

        self.stdout.write('Đang bắt đầu import Vocabulary...')
        
        count = 0
        skipped = 0
        
        # 1. Dùng utf-8-sig để xử lý lỗi BOM nếu file xuất từ Excel
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # --- DEBUG: In ra tên các cột để xem có bị lỗi ký tự lạ không ---
            self.stdout.write(f"Danh sách cột tìm thấy: {reader.fieldnames}")
            
            for index, row in enumerate(reader):
                # 2. Làm sạch dữ liệu topic_id
                raw_topic = row.get('topic', '').strip() # Xóa khoảng trắng thừa
                
                # Bỏ qua dòng tiêu đề lặp lại (nếu có)
                if raw_topic.lower() == 'topic' or not raw_topic:
                    continue

                try:
                    # 3. Tìm Topic (Ép kiểu int để chắc chắn khớp với DB)
                    topic_id = int(raw_topic) 
                    topic_obj = Topic.objects.get(id=topic_id)

                    Vocabulary.objects.update_or_create(
                        word=row.get('word', '').strip(),
                        topic=topic_obj,
                        defaults={
                            'pronunciation': row.get('pronunciation', ''),
                            'word_type': row.get('word_type', ''),
                            'meaning': row.get('meaning', ''),
                            'example_sentence': row.get('example_en', ''),
                            'example_meaning': row.get('example_vi', ''),
                            'image': row.get('image_url', ''),
                            'audio': row.get('audio_url', '')
                        }
                    )
                    count += 1
                    
                except ValueError:
                    # Lỗi này hiện ra nếu cột topic không phải là số (ví dụ là chữ cái)
                    if skipped < 5: # Chỉ in 5 lỗi đầu tiên để đỡ spam
                        self.stdout.write(self.style.WARNING(f"Lỗi dòng {index}: ID Topic không hợp lệ ('{raw_topic}')"))
                    skipped += 1
                except Topic.DoesNotExist:
                    # Lỗi này hiện ra nếu số ID đúng định dạng nhưng không có trong DB
                    if skipped < 5:
                        self.stdout.write(self.style.WARNING(f"Lỗi dòng {index}: Không tìm thấy Topic ID {raw_topic} trong DB"))
                    skipped += 1
                except Exception as e:
                     self.stdout.write(self.style.ERROR(f"Lỗi lạ ở dòng {index}: {e}"))

                if count > 0 and count % 500 == 0:
                    self.stdout.write(f'Đã xử lý {count} từ...')

        self.stdout.write(self.style.SUCCESS(f'Hoàn tất! Thành công: {count}, Bỏ qua: {skipped}.'))