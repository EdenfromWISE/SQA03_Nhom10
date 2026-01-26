from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json

from .actions import (
    handle_chao_hoi,
    handle_lam_quiz,
    handle_tra_tu,
    handle_hoi_chuc_nang,
    handle_gioi_thieu_trang_web,
    handle_phat_am_tu_vung,
)
from .nlu import nlu_processor
from .models import ChatMessage


class ChatbotHistoryView(APIView):
    """API để quản lý lịch sử chat"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lấy lịch sử chat của user"""
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')[:1000]
        
        messages_data = []
        for msg in messages:
            msg_dict = {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
            }
            if msg.message_type:
                msg_dict["type"] = msg.message_type
            if msg.audio_url:
                msg_dict["audio_url"] = msg.audio_url
            if msg.word:
                msg_dict["word"] = msg.word
            if msg.phonetic:
                msg_dict["phonetic"] = msg.phonetic
            
            messages_data.append(msg_dict)
        
        return Response({"messages": messages_data})

    def delete(self, request):
        """Xóa lịch sử chat của user"""
        ChatMessage.objects.filter(user=request.user).delete()
        return Response({"message": "Chat history cleared successfully"})


@method_decorator(csrf_exempt, name="dispatch")
class ChatbotApiEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return Response({"reply": "Bạn chưa nhập nội dung gì cả."}, status=400)

        # 1. Chạy NLU
        nlu_result = nlu_processor.parse(user_message)
        intent = nlu_result["intent"]["name"]
        entities = nlu_result.get("entities", [])

        # 2. Nếu có entity "tu_vung" thì lưu lại vào session
        last_vocab_word = None
        for ent in entities:
            if ent.get("entity") == "tu_vung":
                last_vocab_word = ent.get("value")
                break

        if last_vocab_word:
            request.session["last_vocab_word"] = last_vocab_word
            request.session.modified = True  # Đảm bảo session được lưu

        # 3. Nếu user hỏi "cách đọc" hoặc "tra từ" mà KHÔNG nói từ nào
        #    → lấy lại từ cuối cùng đã lưu trong session
        if intent == "phat_am_tu_vung":
            has_vocab_entity = any(e.get("entity") == "tu_vung" for e in entities)

            if not has_vocab_entity:
                saved_word = request.session.get("last_vocab_word")

                if saved_word:
                    # Bổ sung entity để hàm handle_phat_am_tu_vung dùng như bình thường
                    entities.append(
                        {
                            "entity": "tu_vung",
                            "value": saved_word,
                        }
                    )
                else:
                    # Không có từ nào đã lưu → hỏi lại user
                    return Response(
                        {
                            "reply": "Bạn muốn mình đọc từ nào? Ví dụ: 'cách đọc từ client'."
                        }
                    )

        # Tương tự cho intent "tra_tu"
        if intent == "tra_tu":
            has_vocab_entity = any(e.get("entity") == "tu_vung" for e in entities)

            if not has_vocab_entity:
                saved_word = request.session.get("last_vocab_word")

                if saved_word:
                    # Bổ sung entity để hàm handle_tra_tu dùng như bình thường
                    entities.append(
                        {
                            "entity": "tu_vung",
                            "value": saved_word,
                        }
                    )
                else:
                    # Không có từ nào đã lưu → hỏi lại user
                    return Response(
                        {
                            "reply": "Bạn muốn tra từ nào? Ví dụ: 'từ client là gì'."
                        }
                    )

        # 4. Gọi các action theo intent
        if intent == "tra_tu":
            bot_reply = handle_tra_tu(entities)
        elif intent == "lam_quiz":
            bot_reply = handle_lam_quiz()
        elif intent == "chao_hoi":
            bot_reply = handle_chao_hoi()
        elif intent == "hoi_chuc_nang":
            bot_reply = handle_hoi_chuc_nang()
        elif intent == "gioi_thieu_trang_web":
            bot_reply = handle_gioi_thieu_trang_web()
        elif intent == "phat_am_tu_vung":
            bot_reply = handle_phat_am_tu_vung(entities)
        else:
            bot_reply = "Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể nói rõ hơn không?"

        # 5. Lưu message vào database
        import time
        timestamp = int(time.time() * 1000)
        
        # Xử lý bot_reply nếu là dict (pronunciation)
        if isinstance(bot_reply, dict):
            bot_content = bot_reply.get("message", "")
            bot_type = bot_reply.get("type")
            audio_url = bot_reply.get("audio_url")
            word = bot_reply.get("word")
            phonetic = bot_reply.get("phonetic")
        else:
            bot_content = bot_reply
            bot_type = None
            audio_url = None
            word = None
            phonetic = None
        
        # Lưu user message
        ChatMessage.objects.create(
            user=request.user,
            role="user",
            content=user_message,
            timestamp=timestamp
        )
        
        # Lưu assistant message
        ChatMessage.objects.create(
            user=request.user,
            role="assistant",
            content=bot_content,
            timestamp=timestamp + 1,
            message_type=bot_type,
            audio_url=audio_url,
            word=word,
            phonetic=phonetic
        )
        
        # Giới hạn số lượng messages (xóa các message cũ hơn 1000 messages gần nhất)
        message_count = ChatMessage.objects.filter(user=request.user).count()
        if message_count > 1000:
            # Lấy timestamp của message thứ 1000 từ dưới lên
            messages_to_keep = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:1000]
            if messages_to_keep:
                oldest_timestamp = messages_to_keep[len(messages_to_keep) - 1].timestamp
                ChatMessage.objects.filter(user=request.user, timestamp__lt=oldest_timestamp).delete()

        return Response({"reply": bot_reply})


