"""
Unit tests for chatbot/actions.py
Covers: translate_text_to_vietnamese, handle_tra_tu, handle_lam_quiz,
        handle_phat_am_tu_vung
"""
import pytest
from unittest.mock import patch, MagicMock

from chatbot.actions import (
    translate_text_to_vietnamese,
    handle_tra_tu,
    handle_lam_quiz,
    handle_phat_am_tu_vung,
)
from vocabulary.models import Course, Topic, Vocabulary


@pytest.fixture
def vocab_set(db):
    course = Course.objects.create(title="Test Course")
    topic = Topic.objects.create(course=course, title="Test Topic")
    words = ["apple", "banana", "cherry", "date"]
    vocabs = []
    for w in words:
        v = Vocabulary.objects.create(topic=topic, word=w, meaning=f"nghia cua {w}")
        vocabs.append(v)
    return vocabs


class TestTranslateTextToVietnamese:

    def test_UT_CHB_ACT_001_empty_input_returns_khong_co(self):
        """UT-CHB-ACT-001: Input rỗng → trả 'Không có'."""
        result = translate_text_to_vietnamese("")
        assert result == "Không có"

    def test_no_definition_sentinel_returns_khong_co(self):
        """Input là 'Không tìm thấy định nghĩa.' → trả 'Không có'."""
        result = translate_text_to_vietnamese("Không tìm thấy định nghĩa.")
        assert result == "Không có"

    @patch("chatbot.actions.requests.get")
    def test_UT_CHB_ACT_002_api_exception_returns_original_text(self, mock_get):
        """UT-CHB-ACT-002: requests raise exception → trả lại text gốc."""
        mock_get.side_effect = Exception("Connection error")
        result = translate_text_to_vietnamese("hello")
        assert result == "hello"

    @patch("chatbot.actions.requests.get")
    def test_successful_translation_returns_translated(self, mock_get):
        """Kết nối thành công → trả translatedText từ API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "responseData": {"translatedText": "Xin chào"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = translate_text_to_vietnamese("hello")
        assert result == "Xin chào"


class TestHandleTraTu:

    def test_UT_CHB_ACT_003_missing_tu_vung_entity_asks_user(self):
        """UT-CHB-ACT-003: Không có entity 'tu_vung' → hỏi lại user."""
        result = handle_tra_tu([])
        assert "tra" in result.lower() or "từ" in result.lower() or "Bạn" in result

    def test_handle_tra_tu_with_entity_calls_external_api(self):
        """Có entity 'tu_vung' → gọi dictionary API (mock)."""
        entities = [{"entity": "tu_vung", "value": "hello"}]
        with patch("chatbot.actions.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{
                "word": "hello",
                "phonetic": "/həˈloʊ/",
                "meanings": [{"definitions": [{"definition": "A greeting"}]}]
            }]
            translate_mock = MagicMock()
            translate_mock.return_value = MagicMock(
                status_code=200,
                json=lambda: {"responseData": {"translatedText": "Xin chào"}}
            )
            mock_get.side_effect = [mock_response, translate_mock.return_value, translate_mock.return_value]
            result = handle_tra_tu(entities)
        assert "hello" in result.lower() or "Hello" in result


@pytest.mark.django_db
class TestHandleLamQuiz:

    def test_UT_CHB_ACT_004_less_than_4_vocab_returns_warning_text(self, db):
        """UT-CHB-ACT-004: Vocab < 4 → type='text', message cảnh báo."""
        course = Course.objects.create(title="Small Course")
        topic = Topic.objects.create(course=course, title="Small Topic")
        Vocabulary.objects.create(topic=topic, word="a", meaning="a")
        result = handle_lam_quiz()
        assert result["type"] == "text"
        assert "4" in result["message"] or "quiz" in result["message"].lower()

    def test_UT_CHB_ACT_005_enough_vocab_returns_quiz_offer(self, vocab_set):
        """UT-CHB-ACT-005: Vocab >= 4 → type='quiz_offer', số câu <= 10."""
        result = handle_lam_quiz()
        assert result["type"] == "quiz_offer"
        assert "questions" in result
        assert len(result["questions"]) <= 10
        assert len(result["questions"]) >= 1


class TestHandlePhatAmTuVung:

    def test_UT_CHB_ACT_006_missing_tu_vung_entity_returns_ask_message(self):
        """UT-CHB-ACT-006: Không có entity → hỏi từ cần phát âm."""
        result = handle_phat_am_tu_vung([])
        assert "phát âm" in result.lower() or "từ" in result.lower() or "Bạn" in result

    @patch("chatbot.actions.requests.get")
    def test_with_valid_word_returns_phonetic_info(self, mock_get):
        """Có entity với từ hợp lệ → trả phonetic info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "word": "cat",
            "phonetic": "/kæt/",
            "phonetics": [{"audio": "https://example.com/cat.mp3"}],
        }]
        mock_get.return_value = mock_response
        entities = [{"entity": "tu_vung", "value": "cat"}]
        result = handle_phat_am_tu_vung(entities)
        if isinstance(result, dict):
            assert result.get("type") == "pronunciation"
            assert "audio_url" in result
        else:
            assert "cat" in result.lower() or "kæt" in result
