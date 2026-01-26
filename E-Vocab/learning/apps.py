from django.apps import AppConfig
import sys


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning'

    pronunciation_assessor = None

    def ready(self):
        # Kiểm tra để tránh load model khi chạy các lệnh quản trị như makemigrations
        if 'runserver' in sys.argv or 'uwsgi' in sys.argv:
            from .services.pronunciation_ai import PronunciationAssessor # Import ở đây để tránh lỗi vòng tròn
            
            print(">>> [Django Start] Đang khởi tạo AI Model...")
            LearningConfig.pronunciation_assessor = PronunciationAssessor()
