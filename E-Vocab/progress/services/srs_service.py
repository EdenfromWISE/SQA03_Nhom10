from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from progress.models import UserVocabularyMastery
from vocabulary.models import Vocabulary
from typing import Optional


class SM2Service:
    """
    Service triển khai thuật toán SM-2 (SuperMemo 2) cho SRS.
    Quality: Đúng = 3, Sai = 2
    Chỉ ghi nhận SRS cho từ vựng đến hạn, quá hạn hoặc mới học.
    """

    @staticmethod
    def get_or_create_mastery(user: User, vocabulary: Vocabulary) -> UserVocabularyMastery:
        """
        Lấy hoặc tạo mastery object với giá trị mặc định cho SM-2.
        Từ vựng mới học sẽ có next_review_date = None (để đánh dấu là từ mới).
        """
        mastery, created = UserVocabularyMastery.objects.get_or_create(
            user=user,
            vocabulary=vocabulary,
            defaults={
                "interval": 1,
                "ease_factor": 2.5,
                "repetitions": 0,
                "quality": 0,
                "proficiency": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "next_review_date": None,  # None = từ mới học
            },
        )
        
        return mastery

    @staticmethod
    def is_vocabulary_eligible_for_srs(
        user: User, vocabulary: Vocabulary
    ) -> bool:
        """
        Kiểm tra xem từ vựng có đủ điều kiện để ghi nhận SRS không.
        Trả về True nếu:
        - Từ vựng mới học (chưa có mastery hoặc chưa có next_review_date)
        - Từ vựng đến hạn ôn tập (next_review_date <= now)
        - Từ vựng quá hạn ôn tập (next_review_date < now)
        """
        try:
            mastery = UserVocabularyMastery.objects.get(
                user=user,
                vocabulary=vocabulary
            )
            
            # Nếu chưa có next_review_date, coi như từ mới học
            if mastery.next_review_date is None:
                return True
            
            # Kiểm tra xem đã đến hạn hoặc quá hạn chưa
            now = timezone.now()
            return mastery.next_review_date <= now
            
        except UserVocabularyMastery.DoesNotExist:
            # Chưa có mastery, coi như từ mới học
            return True

    @staticmethod
    def update_review(
        user: User, 
        vocabulary: Vocabulary, 
        is_correct: bool,
        force_update: bool = False
    ) -> Optional[UserVocabularyMastery]:
        """
        Áp dụng thuật toán SM-2 để cập nhật thông tin ôn tập.
        
        Args:
            user: Người dùng
            vocabulary: Từ vựng
            is_correct: True nếu trả lời đúng, False nếu trả lời sai
            force_update: Nếu True, cập nhật bất kể điều kiện (mặc định: False)
        
        Returns:
            UserVocabularyMastery nếu cập nhật thành công, None nếu không đủ điều kiện
        """
        # Kiểm tra điều kiện trừ khi force_update = True
        if not force_update:
            if not SM2Service.is_vocabulary_eligible_for_srs(user, vocabulary):
                return None
        
        mastery = SM2Service.get_or_create_mastery(user, vocabulary)
        
        # Chuyển đổi is_correct sang quality: đúng = 3, sai = 2
        quality = 3 if is_correct else 2
        
        # Lưu quality và thời điểm thực hành
        mastery.quality = quality
        mastery.last_practiced_at = timezone.now()
        
        # 1. Cập nhật thống kê đúng/sai
        if is_correct:
            mastery.correct_count += 1
        else:
            mastery.incorrect_count += 1
        
        # 2. Thuật toán SM-2
        # Nếu trả lời sai (quality < 3), reset về lần ôn đầu tiên
        if quality < 3:
            mastery.repetitions = 0
            mastery.interval = 1
        else:
            # Nếu trả lời đúng, tăng số lần lặp lại và cập nhật interval
            if mastery.repetitions == 0:
                mastery.interval = 1
            elif mastery.repetitions == 1:
                mastery.interval = 6
            else:
                mastery.interval = int(mastery.interval * mastery.ease_factor)
            
            mastery.repetitions += 1
        
        # 3. Cập nhật ease factor theo công thức SM-2
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        # Với q = quality (2 hoặc 3)
        ease_factor_change = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        mastery.ease_factor = mastery.ease_factor + ease_factor_change
        
        # Giới hạn ease factor tối thiểu là 1.3
        if mastery.ease_factor < 1.3:
            mastery.ease_factor = 1.3
        
        # 4. Cập nhật ngày ôn tập tiếp theo
        mastery.next_review_date = timezone.now() + timedelta(days=mastery.interval)
        
        # 5. Cập nhật proficiency (%)
        total = mastery.correct_count + mastery.incorrect_count
        mastery.proficiency = (mastery.correct_count / total) * 100 if total > 0 else 0
        
        # Lưu thay đổi
        mastery.save()
        
        return mastery

    @staticmethod
    def bulk_update(user: User, results: list, force_update: bool = False) -> list:
        """
        Cập nhật SM-2 hàng loạt cho nhiều từ vựng.
        
        Args:
            user: Người dùng
            results: Danh sách dict với format [
                {"vocab_id": 123, "is_correct": True},
                {"vocab_id": 124, "is_correct": False},
                ...
            ]
            force_update: Nếu True, cập nhật bất kể điều kiện (mặc định: False)
        
        Returns:
            Danh sách các mastery đã được cập nhật
        """
        updated = []
        for item in results:
            try:
                vocabulary = Vocabulary.objects.get(id=item["vocab_id"])
                is_correct = item.get("is_correct", False)
                
                mastery = SM2Service.update_review(
                    user=user,
                    vocabulary=vocabulary,
                    is_correct=is_correct,
                    force_update=force_update,
                )
                
                if mastery:
                    updated.append(mastery)
            except Vocabulary.DoesNotExist:
                continue
        
        return updated

    @staticmethod
    def get_vocabularies_due_for_review(user: User, limit: Optional[int] = None) -> list:
        """
        Lấy danh sách từ vựng đến hạn hoặc quá hạn ôn tập.
        
        Args:
            user: Người dùng
            limit: Số lượng tối đa từ vựng trả về (None = không giới hạn)
        
        Returns:
            Danh sách UserVocabularyMastery objects
        """
        now = timezone.now()
        query = UserVocabularyMastery.objects.filter(
            user=user,
            next_review_date__lte=now
        ).order_by('next_review_date')
        
        if limit:
            query = query[:limit]
        
        return list(query)

    @staticmethod
    def get_new_vocabularies(
        user: User, 
        vocabularies: list[Vocabulary]
    ) -> list[Vocabulary]:
        """
        Lấy danh sách từ vựng mới (chưa có mastery hoặc chưa có next_review_date).
        
        Args:
            user: Người dùng
            vocabularies: Danh sách từ vựng cần kiểm tra
        
        Returns:
            Danh sách Vocabulary objects chưa được học
        """
        vocabulary_ids = [v.id for v in vocabularies]
        
        # Lấy các mastery đã có next_review_date
        existing_masteries = UserVocabularyMastery.objects.filter(
            user=user,
            vocabulary_id__in=vocabulary_ids,
            next_review_date__isnull=False
        ).values_list('vocabulary_id', flat=True)
        
        # Lọc ra các từ vựng chưa được học
        new_vocab_ids = set(vocabulary_ids) - set(existing_masteries)
        
        return [v for v in vocabularies if v.id in new_vocab_ids]