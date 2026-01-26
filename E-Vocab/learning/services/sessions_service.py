from __future__ import annotations

from typing import Any, Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from learning.models import LearningSession, Question, UserAnswer, LearningConfig
from learning.services.question_service import QuestionService
from progress.models import UserTopicProgress, UserVocabularyMastery
from vocabulary.models import Topic, Vocabulary
from progress.services.streak_service import StreakService
from progress.services.srs_service import SM2Service
import json


class SessionsService:
    """Service quản lý các phiên học tập (practice, review, exam)."""

    def __init__(self):
        self.question_service = QuestionService()

    def create_practice_session(
        self,
        user: User,
        topic: Topic,
        total_questions: Optional[int] = None,
        question_distribution: Optional[Dict[str, int]] = None,
    ) -> LearningSession:
        """
        Tạo phiên luyện tập cho một topic.

        Args:
            user: Người dùng
            topic: Topic cần luyện tập
            total_questions: Tổng số câu hỏi (mặc định lấy từ config)
            question_distribution: Phân bố số câu hỏi theo loại

        Returns:
            LearningSession: Phiên học tập đã tạo
        """
        config = LearningConfig.get_solo()
        vocabularies = list(topic.vocabularies.all())

        if not vocabularies:
            raise ValueError(f"Topic '{topic.title}' không có từ vựng nào")

        # Sử dụng config mặc định nếu không chỉ định
        if total_questions is None:
            total_questions = min(config.total_questions, len(vocabularies))

        # Tạo session
        session = LearningSession.objects.create(
            user=user,
            topic=topic,
            mode="practice",
            time_limit=config.time_limit,
            total_questions=total_questions,
            pass_score=0,  # Practice không cần pass score
        )

        # Tạo câu hỏi sử dụng QuestionService
        questions_data = self.question_service.generate_session_questions(
            vocabularies=vocabularies,
            total_questions=total_questions,
            question_distribution=question_distribution,
        )

        # Lưu câu hỏi vào database
        self._save_questions_to_session(session, questions_data)

        return session

    def create_review_session(
        self,
        user: User,
        total_questions: Optional[int] = None,
    ) -> LearningSession:
        """
        Tạo phiên ôn tập cho các từ vựng đến hạn/quá hạn theo SRS.

        - Mỗi lần gọi chỉ lấy tối đa 20 từ.
        - Các từ được chọn dựa trên `next_review_date` (đến hạn hoặc quá hạn).
        - Khi người dùng hoàn thành phiên và SRS được cập nhật,
          các từ đã ôn sẽ có `next_review_date` mới và không xuất hiện lại
          trong lần gọi tiếp theo.
        """
        config = LearningConfig.get_solo()

        # Xác định số câu hỏi tối đa (không vượt quá 20)
        if total_questions is None:
            total_questions = config.total_questions
        try:
            total_questions = int(total_questions)
        except (TypeError, ValueError):
            total_questions = config.total_questions

        if total_questions <= 0:
            total_questions = 1

        max_per_session = 20
        limit = min(total_questions, max_per_session)

        # Lấy các từ vựng đến hạn/quá hạn theo SRS
        masteries_due = SM2Service.get_vocabularies_due_for_review(
            user=user,
            limit=limit,
        )

        if not masteries_due:
            raise ValueError("Hiện tại không có từ vựng nào đến hạn ôn tập.")

        vocabularies = [m.vocabulary for m in masteries_due]

        # Đảm bảo total_questions không vượt quá số từ thực tế
        total_questions = min(limit, len(vocabularies))

        # Tạo session ở chế độ review (không gắn với topic cụ thể)
        session = LearningSession.objects.create(
            user=user,
            topic=None,
            mode="review",
            time_limit=config.time_limit,
            total_questions=total_questions,
            pass_score=0,  # Review không cần pass score
        )

        # Tạo câu hỏi dựa trên danh sách vocabulary đã chọn
        questions_data = self.question_service.generate_session_questions(
            vocabularies=vocabularies,
            total_questions=total_questions,
        )

        # Lưu câu hỏi vào database
        self._save_questions_to_session(session, questions_data)

        return session

    def create_exam_session(
        self,
        user: User,
        topic: Topic,
        time_limit: Optional[int] = None,
        total_questions: Optional[int] = None,
        pass_score: Optional[int] = None,
    ) -> LearningSession:
        """
        Tạo phiên kiểm tra cho một topic.

        Args:
            user: Người dùng
            topic: Topic cần kiểm tra
            time_limit: Thời gian giới hạn (phút)
            total_questions: Tổng số câu hỏi
            pass_score: Điểm đạt (%)

        Returns:
            LearningSession: Phiên học tập đã tạo
        """
        config = LearningConfig.get_solo()
        vocabularies = list(topic.vocabularies.all())

        if not vocabularies:
            raise ValueError(f"Topic '{topic.title}' không có từ vựng nào")

        # Kiểm tra số lần thi trong ngày
        today = timezone.now().date()
        today_exams = LearningSession.objects.filter(
            user=user,
            topic=topic,
            mode="exam",
            started_at__date=today,
        ).count()

        if today_exams >= config.max_daily_exams_per_topic:
            raise ValueError(
                f"Bạn đã đạt giới hạn {config.max_daily_exams_per_topic} lần thi/ngày cho topic này"
            )

        # Sử dụng config mặc định nếu không chỉ định
        if time_limit is None:
            time_limit = config.time_limit
        if total_questions is None:
            total_questions = min(config.total_questions, len(vocabularies))
        if pass_score is None:
            pass_score = config.pass_score

        # Tạo session
        session = LearningSession.objects.create(
            user=user,
            topic=topic,
            mode="exam",
            time_limit=time_limit,
            total_questions=total_questions,
            pass_score=pass_score,
        )

        # Tạo câu hỏi
        questions_data = self.question_service.generate_session_questions(
            vocabularies=vocabularies,
            total_questions=total_questions,
        )

        # Lưu câu hỏi
        self._save_questions_to_session(session, questions_data)

        return session

    def submit_answer(
        self,
        session: LearningSession,
        question_id: int,
        user_answer: Any,
        pronunciation_score: Optional[float] = None,
        time_spent: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Tiếp nhận và đánh giá câu trả lời của người dùng.

        Args:
            session: Phiên học tập
            question_id: ID của câu hỏi
            user_answer: Câu trả lời của người dùng
            pronunciation_score: Điểm phát âm (chỉ dùng cho speaking)
            time_spent: Thời gian làm câu hỏi (giây)

        Returns:
            Dict với kết quả đánh giá
        """
        if session.completed_at:
            raise ValueError("Phiên học tập đã hoàn thành")

        try:
            question = Question.objects.get(id=question_id, session=session)
        except Question.DoesNotExist:
            raise ValueError(f"Câu hỏi {question_id} không tồn tại trong phiên này")

        # Lấy thông tin câu hỏi từ content và thêm type + answer
        question_data = question.content.copy()
        question_data["type"] = question.question_type
        question_data["answer"] = question.correct_answer

        # Đánh giá câu trả lời sử dụng QuestionService
        evaluation = self.question_service.evaluate_answer(
            user_answer=user_answer,
            question=question_data,
            pronunciation_score=pronunciation_score,
        )

        # Xác định cách lưu answer_text và selected_option
        answer_text = None
        selected_option = None

        if isinstance(user_answer, (dict, list)):
            # Với matching question (dict) hoặc các câu trả lời dạng list/dict
            answer_text = json.dumps(user_answer, ensure_ascii=False)
        elif isinstance(user_answer, str):
            # Với writing/speaking question (string)
            answer_text = user_answer
        elif isinstance(user_answer, (int, float)):
            # Với reading/listening question (index)
            selected_option = str(user_answer)

        # Lưu câu trả lời
        user_answer_obj, created = UserAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                "selected_option": selected_option,
                "answer_text": answer_text,
                "is_correct": evaluation["is_correct"],
                "time_spent": time_spent,
            },
        )

        return {
            "answer_id": user_answer_obj.id,
            "is_correct": evaluation["is_correct"],
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
        }

    def complete_session(
        self,
        session: LearningSession,
    ) -> Dict[str, Any]:
        """
        Hoàn thành phiên học tập và tính điểm.

        Args:
            session: Phiên học tập cần hoàn thành

        Returns:
            Dict với kết quả phiên học tập
        """
        if session.completed_at:
            raise ValueError("Phiên học tập đã hoàn thành")

        questions = session.questions.all()
        user_answers = {ua.question_id: ua for ua in session.user_answers.all()}

        # Tính điểm
        total_questions = questions.count()
        correct_count = sum(
            1
            for q in questions
            if user_answers.get(q.id) and user_answers[q.id].is_correct
        )

        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        is_passed = score >= session.pass_score

        # Cập nhật session
        session.score = score
        session.is_passed = is_passed
        session.completed_at = timezone.now()
        session.save()

        # Cập nhật tiến độ cho TẤT CẢ các mode (practice, review, exam)
        with transaction.atomic():
            self._update_progress_after_session(session, questions, user_answers)

        return {
            "session_id": session.id,
            "score": round(score, 2),
            "correct_count": correct_count,
            "total_count": total_questions,
            "is_passed": is_passed,
            "completed_at": session.completed_at,
        }

    def cancel_session(self, session: LearningSession) -> None:
        """
        Hủy bỏ phiên học tập.

        Args:
            session: Phiên học tập cần hủy
        """
        if session.completed_at:
            raise ValueError("Không thể hủy phiên học tập đã hoàn thành")

        session.delete()

    def _save_questions_to_session(
        self,
        session: LearningSession,
        questions_data: List[Dict[str, Any]],
    ) -> None:
        """Lưu danh sách câu hỏi vào session."""
        questions_to_create = []

        for order, question_data in enumerate(questions_data, start=1):
            # Lấy vocabulary_id từ metadata hoặc từ question_data
            vocabulary_id = question_data.get("metadata", {}).get("vocabulary_id")
            if not vocabulary_id:
                vocabulary_id = question_data.get("vocabulary_id")

            # Tách prompt và answer từ question_data
            prompt = question_data.get("prompt", {})
            answer = question_data.get("answer", question_data.get("correct_answer"))

            questions_to_create.append(
                Question(
                    session=session,
                    vocabulary_id=vocabulary_id,
                    question_type=question_data["type"],
                    order=order,
                    content={
                        "id": question_data.get("id"),
                        "title": question_data.get("title"),
                        "prompt": prompt,
                    },
                    correct_answer=answer,
                    explanation=question_data.get("explanation", ""),
                )
            )

        Question.objects.bulk_create(questions_to_create)

    def _update_progress_after_session(
        self,
        session: LearningSession,
        questions: List[Question],
        user_answers: Dict[int, UserAnswer],
    ) -> None:
        """
        Cập nhật tiến độ học tập sau khi hoàn thành session.
        - Cập nhật SRS (SM-2) cho các từ vựng đến hạn/quá hạn/mới học
        - Cập nhật UserTopicProgress cho exam mode
        """
        # Cập nhật streak
        StreakService.update_streak(session.user)

        # Cập nhật SRS cho từng vocabulary
        for question in questions:
            if not question.vocabulary:
                continue

            user_answer_obj = user_answers.get(question.id)
            if not user_answer_obj:
                continue

            # Chỉ cập nhật SRS nếu từ vựng đến hạn/quá hạn/mới học
            # SM2Service sẽ tự động kiểm tra điều kiện
            SM2Service.update_review(
                user=session.user,
                vocabulary=question.vocabulary,
                is_correct=user_answer_obj.is_correct,
                force_update=False,  # Chỉ cập nhật nếu đủ điều kiện
            )

        if not session.topic:
            return

        # Nếu là exam mode, cập nhật thêm UserTopicProgress
        if session.mode == "exam":
            topic_progress, created = UserTopicProgress.objects.get_or_create(
                user=session.user,
                topic=session.topic,
            )

            if not created:
                topic_progress.attempts += 1
                topic_progress.last_attempt_at = timezone.now()

                if session.is_passed and session.score > topic_progress.best_score:
                    topic_progress.best_score = session.score
                    topic_progress.is_passed = True

                topic_progress.save()
            else:
                # Nếu mới tạo, set các giá trị ban đầu
                topic_progress.attempts = 1
                topic_progress.last_attempt_at = timezone.now()
                topic_progress.best_score = session.score if session.is_passed else 0
                topic_progress.is_passed = session.is_passed
                topic_progress.save()

            # Kiểm tra và cập nhật course progress
            if session.topic.course:
                course_progress = session.user.course_progress.filter(
                    course=session.topic.course
                ).first()

                if course_progress:
                    course_progress.check_completion()
