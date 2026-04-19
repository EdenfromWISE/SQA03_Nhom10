"""
Unit tests for chatbot/views.py
Covers: ChatbotHistoryView (get, delete), ChatbotApiEndpoint (post)
"""
import pytest
from unittest.mock import patch, MagicMock

from chatbot.models import ChatMessage

HISTORY_URL = "/api/history/"
CHAT_URL = "/api/chat/"


@pytest.mark.django_db
class TestChatbotHistoryViewGet:

    def test_UT_CHB_HIS_001_get_returns_only_current_user_messages_in_order(
        self, auth_client, user, user2, auth_client2
    ):
        """UT-CHB-HIS-001: GET trả lịch sử user hiện tại, đúng thứ tự timestamp."""
        ChatMessage.objects.create(user=user, role="user", content="Hi", timestamp=1000)
        ChatMessage.objects.create(user=user, role="assistant", content="Hello", timestamp=1001)
        ChatMessage.objects.create(user=user2, role="user", content="Other", timestamp=500)

        response = auth_client.get(HISTORY_URL)
        assert response.status_code == 200
        messages = response.data["messages"]
        assert len(messages) == 2
        contents = [m["content"] for m in messages]
        assert "Hi" in contents
        assert "Hello" in contents
        assert "Other" not in contents
        timestamps = [m["timestamp"] for m in messages]
        assert timestamps == sorted(timestamps)

    def test_unauthenticated_get_returns_401(self, api_client):
        """Anonymous user không thể truy cập lịch sử."""
        response = api_client.get(HISTORY_URL)
        assert response.status_code in (401, 403)


@pytest.mark.django_db
class TestChatbotHistoryViewDelete:

    def test_UT_CHB_HIS_002_delete_clears_only_current_user_history(
        self, auth_client, user, user2
    ):
        """UT-CHB-HIS-002: DELETE xóa lịch sử user hiện tại, không ảnh hưởng user khác."""
        ChatMessage.objects.create(user=user, role="user", content="Msg1", timestamp=100)
        ChatMessage.objects.create(user=user2, role="user", content="Msg2", timestamp=200)

        response = auth_client.delete(HISTORY_URL)
        assert response.status_code == 200
        assert ChatMessage.objects.filter(user=user).count() == 0
        assert ChatMessage.objects.filter(user=user2).count() == 1


@pytest.mark.django_db
class TestChatbotApiEndpointPost:

    NLU_RESULT_CHAO = {"intent": {"name": "chao_hoi"}, "entities": []}
    NLU_RESULT_TRA_TU = {
        "intent": {"name": "tra_tu"},
        "entities": [{"entity": "tu_vung", "value": "apple"}],
    }

    def _mock_nlu(self, nlu_result):
        return patch("chatbot.views.nlu_processor.parse", return_value=nlu_result)

    def test_UT_CHB_API_001_empty_message_returns_400(self, auth_client):
        """UT-CHB-API-001: Message rỗng/whitespace → 400."""
        with self._mock_nlu(self.NLU_RESULT_CHAO):
            response = auth_client.post(CHAT_URL, {"message": "   "}, format="json")
        assert response.status_code == 400

    def test_UT_CHB_API_003_valid_message_saves_two_chat_messages(self, auth_client, user):
        """UT-CHB-API-003: Message hợp lệ → tạo 2 ChatMessage (user + assistant)."""
        with self._mock_nlu(self.NLU_RESULT_CHAO):
            response = auth_client.post(CHAT_URL, {"message": "Xin chào"}, format="json")
        assert response.status_code == 200
        msgs = ChatMessage.objects.filter(user=user)
        assert msgs.count() == 2
        roles = set(msgs.values_list("role", flat=True))
        assert roles == {"user", "assistant"}

    def test_UT_CHB_API_002_last_vocab_word_used_when_intent_needs_it(self, auth_client, user):
        """UT-CHB-API-002: session có last_vocab_word, intent tra_tu không có entity → dùng word từ session."""
        session = auth_client.session
        session["last_vocab_word"] = "apple"
        session.save()

        nlu_no_entity = {"intent": {"name": "tra_tu"}, "entities": []}
        with self._mock_nlu(nlu_no_entity):
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
                response = auth_client.post(CHAT_URL, {"message": "tra tu do"}, format="json")
        assert response.status_code == 200

    def test_UT_CHB_API_004_old_messages_trimmed_when_exceeding_1000(self, auth_client, user):
        """UT-CHB-API-004: Vượt 1000 messages → trim, tổng <= 1000."""
        # Tạo 1000 messages với timestamp tăng dần
        messages = [
            ChatMessage(user=user, role="user", content=f"msg{i}", timestamp=i)
            for i in range(1000)
        ]
        ChatMessage.objects.bulk_create(messages)

        with self._mock_nlu(self.NLU_RESULT_CHAO):
            auth_client.post(CHAT_URL, {"message": "Hello"}, format="json")

        assert ChatMessage.objects.filter(user=user).count() <= 1000
