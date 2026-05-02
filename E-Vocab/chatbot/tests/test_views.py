"""
chatbot/tests/test_views.py
Unit tests cho chatbot/views.py

Test Cases:
    UT-CHB-HIS-001 — ChatbotHistoryView GET: chỉ trả messages của user hiện tại, đúng thứ tự
    UT-CHB-HIS-002 — ChatbotHistoryView DELETE: xóa lịch sử user hiện tại, giữ user khác
    UT-CHB-HIS-003 — ChatbotHistoryView GET: anonymous user → 401/403
    UT-CHB-API-001 — ChatbotApiEndpoint POST: message rỗng → 400
    UT-CHB-API-002 — ChatbotApiEndpoint POST: session có last_vocab_word → dùng khi intent thiếu entity
    UT-CHB-API-003 — ChatbotApiEndpoint POST: message hợp lệ → tạo 2 ChatMessage
    UT-CHB-API-004 — ChatbotApiEndpoint POST: vượt 1000 messages → trim

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
"""
import pytest
from unittest.mock import patch, MagicMock

from chatbot.models import ChatMessage

HISTORY_URL = "/api/history/"
CHAT_URL    = "/api/chat/"


# ══════════════════════════════════════════════════════════════════════════════
# ChatbotHistoryView — GET
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestChatbotHistoryViewGet:

    # ── UT-CHB-HIS-001 ─────────────────────────────────────────────────────
    def test_UT_CHB_HIS_001_get_returns_only_current_user_messages_in_order(
        self, auth_client, user, user2, auth_client2
    ):
        # TC: UT-CHB-HIS-001 — GET trả lịch sử user hiện tại, đúng thứ tự timestamp
        # [Arrange] Tạo 2 messages cho user, 1 message cho user2
        ChatMessage.objects.create(user=user, role="user",      content="Hi",    timestamp=1000)
        ChatMessage.objects.create(user=user, role="assistant", content="Hello", timestamp=1001)
        ChatMessage.objects.create(user=user2, role="user",     content="Other", timestamp=500)

        # [CheckDB] Xác nhận số lượng messages trong DB
        assert ChatMessage.objects.filter(user=user).count()  == 2
        assert ChatMessage.objects.filter(user=user2).count() == 1

        # [Act]
        response = auth_client.get(HISTORY_URL)

        # [Assert Response] Chỉ thấy 2 messages của user, không lẫn user2
        assert response.status_code == 200
        messages = response.data["messages"]
        assert len(messages) == 2
        contents = [m["content"] for m in messages]
        assert "Hi"    in contents
        assert "Hello" in contents
        assert "Other" not in contents, "Message của user2 không được trả về"

        # [Assert Order] Messages phải theo thứ tự timestamp tăng dần
        timestamps = [m["timestamp"] for m in messages]
        assert timestamps == sorted(timestamps), "Messages phải sắp xếp theo timestamp ASC"
        # [Rollback] ChatMessages sẽ bị rollback sau test

    # ── UT-CHB-HIS-003 ─────────────────────────────────────────────────────
    def test_UT_CHB_HIS_003_unauthenticated_get_returns_401_or_403(self, api_client):
        # TC: UT-CHB-HIS-003 — Anonymous user GET /history → 401 hoặc 403
        # [Act] Anonymous user gọi lịch sử
        response = api_client.get(HISTORY_URL)

        # [Assert] Phải bị từ chối
        assert response.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════════════════════
# ChatbotHistoryView — DELETE
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestChatbotHistoryViewDelete:

    # ── UT-CHB-HIS-002 ─────────────────────────────────────────────────────
    def test_UT_CHB_HIS_002_delete_clears_only_current_user_history(
        self, auth_client, user, user2
    ):
        # TC: UT-CHB-HIS-002 — DELETE xóa lịch sử user hiện tại, không ảnh hưởng user khác
        # [Arrange] Mỗi user có 1 message
        ChatMessage.objects.create(user=user,  role="user", content="Msg1", timestamp=100)
        ChatMessage.objects.create(user=user2, role="user", content="Msg2", timestamp=200)

        # [CheckDB] Xác nhận cả 2 messages tồn tại trước khi DELETE
        assert ChatMessage.objects.filter(user=user).count()  == 1
        assert ChatMessage.objects.filter(user=user2).count() == 1

        # [Act]
        response = auth_client.delete(HISTORY_URL)

        # [Assert Response]
        assert response.status_code == 200

        # [CheckDB] Messages của user bị xóa, messages của user2 vẫn còn
        assert ChatMessage.objects.filter(user=user).count()  == 0, "Lịch sử user phải bị xóa"
        assert ChatMessage.objects.filter(user=user2).count() == 1, "Lịch sử user2 KHÔNG được xóa"
        # [Rollback] user2's messages sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# ChatbotApiEndpoint — POST
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestChatbotApiEndpointPost:

    NLU_CHAO = {"intent": {"name": "chao_hoi"}, "entities": []}
    NLU_TRA_TU_NO_ENTITY = {"intent": {"name": "tra_tu"}, "entities": []}

    def _mock_nlu(self, nlu_result):
        """Helper: patch nlu_processor.parse để không cần model NLU thật."""
        return patch("chatbot.views.nlu_processor.parse", return_value=nlu_result)

    # ── UT-CHB-API-001 ─────────────────────────────────────────────────────
    def test_UT_CHB_API_001_empty_message_returns_400(self, auth_client):
        # TC: UT-CHB-API-001 — Message rỗng/whitespace → 400 Bad Request
        # [Arrange] Message chỉ là khoảng trắng
        with self._mock_nlu(self.NLU_CHAO):
            # [Act]
            response = auth_client.post(CHAT_URL, {"message": "   "}, format="json")

        # [Assert]
        assert response.status_code == 400

    # ── UT-CHB-API-003 ─────────────────────────────────────────────────────
    def test_UT_CHB_API_003_valid_message_saves_two_chat_messages(self, auth_client, user):
        # TC: UT-CHB-API-003 — Message hợp lệ → tạo đúng 2 ChatMessage (user + assistant)
        # [CheckDB] Chưa có ChatMessage trước khi gửi
        assert ChatMessage.objects.filter(user=user).count() == 0

        with self._mock_nlu(self.NLU_CHAO):
            # [Act]
            response = auth_client.post(CHAT_URL, {"message": "Xin chào"}, format="json")

        # [Assert Response]
        assert response.status_code == 200

        # [CheckDB] Phải có đúng 2 messages: 1 user + 1 assistant
        msgs  = ChatMessage.objects.filter(user=user)
        assert msgs.count() == 2, "Phải tạo 2 ChatMessage sau mỗi lượt chat"
        roles = set(msgs.values_list("role", flat=True))
        assert roles == {"user", "assistant"}, "Phải có đúng role 'user' và 'assistant'"
        # [Rollback] ChatMessages sẽ bị rollback sau test

    # ── UT-CHB-API-002 ─────────────────────────────────────────────────────
    def test_UT_CHB_API_002_last_vocab_word_used_when_intent_needs_it(self, auth_client, user):
        # TC: UT-CHB-API-002 — session có last_vocab_word, intent tra_tu không có entity → dùng word từ session
        # [Arrange] Đặt last_vocab_word trong session
        session = auth_client.session
        session["last_vocab_word"] = "apple"
        session.save()

        with self._mock_nlu(self.NLU_TRA_TU_NO_ENTITY):
            with patch("chatbot.actions.requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = [{
                    "word": "apple",
                    "phonetic": "/ˈæpl/",
                    "meanings": [{"definitions": [{"definition": "A fruit"}]}]
                }]
                translate_mock = MagicMock(
                    status_code=200,
                    json=lambda: {"responseData": {"translatedText": "quả táo"}}
                )
                mock_get.side_effect = [mock_response, translate_mock, translate_mock]

                # [Act]
                response = auth_client.post(CHAT_URL, {"message": "tra tu do"}, format="json")

        # [Assert] Không lỗi — "apple" từ session được dùng làm entity
        assert response.status_code == 200

    # ── UT-CHB-API-004 ─────────────────────────────────────────────────────
    def test_UT_CHB_API_004_old_messages_trimmed_when_exceeding_1000(self, auth_client, user):
        # TC: UT-CHB-API-004 — Vượt 1000 messages → trim, tổng ChatMessage của user <= 1000
        # [Arrange] Tạo trước 1000 messages (dùng bulk_create để nhanh)
        messages = [
            ChatMessage(user=user, role="user", content=f"msg{i}", timestamp=i)
            for i in range(1000)
        ]
        ChatMessage.objects.bulk_create(messages)

        # [CheckDB] Xác nhận có đúng 1000 messages trước khi gửi thêm
        assert ChatMessage.objects.filter(user=user).count() == 1000

        with self._mock_nlu(self.NLU_CHAO):
            # [Act] Gửi thêm 1 message → sẽ vượt ngưỡng, cần trim
            auth_client.post(CHAT_URL, {"message": "Hello"}, format="json")

        # [CheckDB] Sau khi trim, tổng phải <= 1000
        total = ChatMessage.objects.filter(user=user).count()
        assert total <= 1000, f"Sau trim phải <= 1000 nhưng có {total}"
        # [Rollback] Tất cả ChatMessages sẽ bị rollback sau test
