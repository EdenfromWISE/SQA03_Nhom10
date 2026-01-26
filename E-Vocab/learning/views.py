from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
import os

# Sửa import: dùng learning.models thay vì exams.models
from learning.models import LearningSession, Question, UserAnswer
from learning.services.sessions_service import SessionsService
from learning.serializers import LearningSessionSerializer
from vocabulary.models import Topic


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_practice_session(request):
    """Tạo phiên luyện tập mới."""
    try:
        topic_id = request.data.get("topic_id")
        if not topic_id:
            return Response(
                {"error": "topic_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        topic = get_object_or_404(Topic, id=topic_id)
        
        service = SessionsService()
        session = service.create_practice_session(
            user=request.user,
            topic=topic,
        )
        
        return Response({
            "session_id": session.id,
            "topic": {"id": topic.id, "title": topic.title},
            "mode": session.mode,
            "total_questions": session.total_questions,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review_session(request):
    """Tạo phiên ôn tập từ vựng theo SRS (tối đa 20 từ đến hạn/quá hạn)."""
    try:
        total_questions = request.data.get("total_questions")

        service = SessionsService()
        session = service.create_review_session(
            user=request.user,
            total_questions=total_questions,
        )

        return Response(
            {
                "session_id": session.id,
                "topic": None,
                "mode": session.mode,
                "time_limit": session.time_limit,
                "total_questions": session.total_questions,
            }
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_exam_session(request):
    """Tạo phiên kiểm tra mới."""
    try:
        topic_id = request.data.get("topic_id")
        if not topic_id:
            return Response(
                {"error": "topic_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        topic = get_object_or_404(Topic, id=topic_id)
        
        service = SessionsService()
        session = service.create_exam_session(
            user=request.user,
            topic=topic,
            time_limit=request.data.get("time_limit"),
            total_questions=request.data.get("total_questions"),
            pass_score=request.data.get("pass_score"),
        )
        
        return Response({
            "session_id": session.id,
            "topic": {"id": topic.id, "title": topic.title},
            "mode": session.mode,
            "time_limit": session.time_limit,
            "total_questions": session.total_questions,
            "pass_score": session.pass_score,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_session(request, session_id):
    """Lấy thông tin phiên học tập."""
    try:
        session = LearningSession.objects.get(id=session_id, user=request.user)
        
        return Response({
            "id": session.id,
            "topic": {"id": session.topic.id, "title": session.topic.title} if session.topic else None,
            "mode": session.mode,
            "time_limit": session.time_limit,
            "total_questions": session.total_questions,
            "pass_score": session.pass_score,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "score": session.score,
            "is_passed": session.is_passed,
        })
    except LearningSession.DoesNotExist:
        return Response(
            {"error": "Phiên học tập không tồn tại"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_session_detail(request, session_id):
    """Lấy chi tiết đầy đủ của phiên học tập (bao gồm questions và user_answers)."""
    try:
        session = LearningSession.objects.prefetch_related('questions', 'user_answers', 'questions__vocabulary').get(
            id=session_id, 
            user=request.user
        )
        
        serializer = LearningSessionSerializer(session)
        return Response(serializer.data)
    except LearningSession.DoesNotExist:
        return Response(
            {"error": "Phiên học tập không tồn tại"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_questions(request, session_id):
    """Lấy danh sách câu hỏi của phiên học tập."""
    try:
        session = LearningSession.objects.get(id=session_id, user=request.user)

        if session.completed_at:
            return Response(
                {"error": "Phiên học tập đã hoàn thành"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        questions = session.questions.all()
        questions_data = [
            {
                "id": question.id,
                "type": question.question_type,
                "content": question.content,
                "order": question.order,
            }
            for question in questions
        ]

        return Response({
            "session": {
                "id": session.id,
                "topic": {"id": session.topic.id, "title": session.topic.title} if session.topic else None,
                "time_limit": session.time_limit,
                "total_questions": session.total_questions,
                "pass_score": session.pass_score,
                "started_at": session.started_at,
            },
            "questions": questions_data,
        })
    except LearningSession.DoesNotExist:
        return Response(
            {"error": "Phiên học tập không tồn tại"}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_answer(request, session_id):
    """Gửi câu trả lời cho một câu hỏi."""
    try:
        session = LearningSession.objects.get(id=session_id, user=request.user)
        
        if session.completed_at:
            return Response(
                {"error": "Phiên học tập đã hoàn thành"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question_id = request.data.get("question_id")
        user_answer = request.data.get("answer")
        time_spent = request.data.get("time_spent", 0.0)
        pronunciation_score = request.data.get("pronunciation_score")
        
        service = SessionsService()
        result = service.submit_answer(
            session=session,
            question_id=question_id,
            user_answer=user_answer,
            pronunciation_score=pronunciation_score,
            time_spent=time_spent,
        )
        
        return Response(result)
    except LearningSession.DoesNotExist:
        return Response(
            {"error": "Phiên học tập không tồn tại"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_session(request, session_id):
    """Hoàn thành phiên học tập."""
    try:
        session = LearningSession.objects.get(id=session_id, user=request.user)
        
        service = SessionsService()
        result = service.complete_session(session)
        
        return Response(result)
    except LearningSession.DoesNotExist:
        return Response(
            {"error": "Phiên học tập không tồn tại"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_session(request, session_id):
    """Hủy phiên học tập."""
    try:
        session = LearningSession.objects.get(id=session_id, user=request.user)
        
        if session.completed_at:
            return Response(
                {"error": "Không thể hủy phiên học tập đã hoàn thành"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = SessionsService()
        service.cancel_session(session)
        
        return Response({"message": "Phiên học tập đã được hủy"})
    except LearningSession.DoesNotExist:
        return Response(
            {"error": "Phiên học tập không tồn tại"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_session_history(request):
    """Lấy lịch sử các phiên học tập của người dùng."""
    try:
        mode = request.query_params.get("mode")  # practice, exam, review, hoặc None (tất cả)
        limit = int(request.query_params.get("limit", 20))
        
        sessions = LearningSession.objects.filter(user=request.user)
        
        if mode:
            sessions = sessions.filter(mode=mode)
        
        sessions = sessions.order_by("-started_at")[:limit]
        
        sessions_data = [
            {
                "id": session.id,
                "topic": {"id": session.topic.id, "title": session.topic.title} if session.topic else None,
                "mode": session.mode,
                "time_limit": session.time_limit,
                "total_questions": session.total_questions,
                "pass_score": session.pass_score,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
                "score": session.score,
                "is_passed": session.is_passed,
            }
            for session in sessions
        ]
        
        return Response({"sessions": sessions_data})
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assess_pronunciation(request):
    """
    API đánh giá phát âm từ file audio.
    Giống như practice/views.py nhưng sử dụng pronunciation_assessor từ learning app.
    """
    try:
        audio_file = request.FILES.get('audio_file')
        target_word = request.POST.get('word', '').strip().lower()
        
        if not audio_file or not target_word:
            return JsonResponse(
                {'error': 'Thiếu file âm thanh hoặc từ mẫu.'}, 
                status=400
            )
        
        # Lấy pronunciation_assessor từ learning app
        from django.apps import apps
        learning_app = apps.get_app_config('learning')
        assessor = learning_app.pronunciation_assessor
        
        if assessor is None:
            return JsonResponse(
                {'error': 'Hệ thống đánh giá phát âm chưa sẵn sàng.'}, 
                status=503
            )
        
        # Lưu file tạm
        fs = FileSystemStorage()
        filename = fs.save(audio_file.name, audio_file)
        audio_path = fs.path(filename)
        
        # Kiểm tra file đã được lưu thành công
        if not os.path.exists(audio_path):
            return JsonResponse(
                {'error': f'Không thể lưu file audio: {audio_path}'}, 
                status=500
            )
        
        try:
            # Đánh giá phát âm
            phoneme_results, overall_score = assessor.get_assessment(audio_path, target_word)
            
            response_data = {
                'word': target_word,
                'phonemes': phoneme_results,
                'score': overall_score
            }
            
            return JsonResponse(response_data, status=200)
        except Exception as ex:
            import traceback
            print(f"[ERROR] assess_pronunciation: {ex}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return JsonResponse(
                {'error': f'Xử lý AI bị lỗi: {str(ex)}'}, 
                status=500
            )
        finally:
            # Xóa file tạm sau khi xử lý xong
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    print(f"[WARNING] Không thể xóa file tạm {audio_path}: {e}")
    except Exception as e:
        return JsonResponse(
            {'error': f'Lỗi xử lý: {str(e)}'}, 
            status=500
        )

