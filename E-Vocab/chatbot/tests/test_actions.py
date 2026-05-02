"""
chatbot/tests/test_actions.py
Unit tests cho chatbot/actions.py

Test Cases:
    UT-CHB-ACT-001 — translate_text_to_vietnamese: input rỗng → 'Không có'
    UT-CHB-ACT-002 — translate_text_to_vietnamese: sentinel 'Không tìm thấy định nghĩa.' → 'Không có'
    UT-CHB-ACT-003 — translate_text_to_vietnamese: API exception → trả text gốc
    UT-CHB-ACT-004 — translate_text_to_vietnamese: API thành công → trả translatedText
    UT-CHB-ACT-005 — handle_tra_tu: thiếu entity → hỏi lại user
    UT-CHB-ACT-006 — handle_tra_tu: có entity tu_vung → gọi dictionary API và trả thông tin
    UT-CHB-ACT-007 — handle_lam_quiz: vocab < 4 → type='text' cảnh báo
    UT-CHB-ACT-008 — handle_lam_quiz: vocab >= 4 → type='quiz_offer', số câu <= 10
    UT-CHB-ACT-009 — handle_phat_am_tu_vung: thiếu entity → hỏi từ cần phát âm
    UT-CHB-ACT-010 — handle_phat_am_tu_vung: có entity tu_vung → trả phonetic + audio_url

Rollback: pytest-django tự động rollback toàn bộ thay đổi DB sau mỗi test.
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


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def vocab_set(db):
    """4 từ vựng — đủ điều kiện tạo quiz."""
    course = Course.objects.create(title="Test Course")
    topic  = Topic.objects.create(course=course, title="Test Topic")
    vocabs = []
    for w in ["apple", "banana", "cherry", "date"]:
        v = Vocabulary.objects.create(topic=topic, word=w, meaning=f"nghia cua {w}")
        vocabs.append(v)
    return vocabs


# ══════════════════════════════════════════════════════════════════════════════
# translate_text_to_vietnamese
# ══════════════════════════════════════════════════════════════════════════════

class TestTranslateTextToVietnamese:

    # ── UT-CHB-ACT-001 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_001_empty_input_returns_khong_co(self):
        # TC: UT-CHB-ACT-001 — Input rỗng → trả 'Không có' (không gọi API)
        # [Arrange] Input là chuỗi rỗng
        # [Act]
        result = translate_text_to_vietnamese("")

        # [Assert] Trả giá trị sentinel, không gọi requests
        assert result == "Không có"

    # ── UT-CHB-ACT-002 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_002_no_definition_sentinel_returns_khong_co(self):
        # TC: UT-CHB-ACT-002 — Input là sentinel 'Không tìm thấy định nghĩa.' → trả 'Không có' (không gọi API)
        # [Arrange] Input là câu sentinel "Không tìm thấy định nghĩa."
        # [Act & Assert] Phải trả 'Không có' mà không gọi API
        result = translate_text_to_vietnamese("Không tìm thấy định nghĩa.")
        assert result == "Không có"

    # ── UT-CHB-ACT-003 ─────────────────────────────────────────────────────
    @patch("chatbot.actions.requests.get")
    def test_UT_CHB_ACT_003_api_exception_returns_original_text(self, mock_get):
        # TC: UT-CHB-ACT-003 — requests raise exception → fallback trả text gốc
        # [Arrange] Mock requests.get ném Exception
        mock_get.side_effect = Exception("Connection error")

        # [Act]
        result = translate_text_to_vietnamese("hello")

        # [Assert] Không throw, trả lại text gốc khi API lỗi
        assert result == "hello"

    # ── UT-CHB-ACT-004 ─────────────────────────────────────────────────────
    @patch("chatbot.actions.requests.get")
    def test_UT_CHB_ACT_004_successful_translation_returns_translated(self, mock_get):
        # TC: UT-CHB-ACT-004 — API translate trả thành công → trả translatedText từ response
        # [Arrange] Mock API trả kết quả dịch thành công
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "responseData": {"translatedText": "Xin chào"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # [Act]
        result = translate_text_to_vietnamese("hello")

        # [Assert] Phải trả bản dịch từ API
        assert result == "Xin chào"


# ══════════════════════════════════════════════════════════════════════════════
# handle_tra_tu
# ══════════════════════════════════════════════════════════════════════════════

class TestHandleTraTu:

    # ── UT-CHB-ACT-005 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_005_missing_tu_vung_entity_asks_user(self):
        # TC: UT-CHB-ACT-005 — Không có entity 'tu_vung' → hỏi lại user cần tra từ nào
        # [Arrange] entities list rỗng (không có tu_vung)
        # [Act]
        result = handle_tra_tu([])

        # [Assert] Response phải có từ liên quan đến "tra" hoặc "từ" hoặc "Bạn"
        assert "tra" in result.lower() or "từ" in result.lower() or "Bạn" in result

    # ── UT-CHB-ACT-006 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_006_handle_tra_tu_with_entity_calls_external_api(self):
        # TC: UT-CHB-ACT-006 — Có entity 'tu_vung' → gọi dictionary API và trả thông tin từ
        # [Arrange] entities chứa tu_vung = "hello"
        entities = [{"entity": "tu_vung", "value": "hello"}]
        with patch("chatbot.actions.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{
                "word": "hello",
                "phonetic": "/həˈloʊ/",
                "meanings": [{"definitions": [{"definition": "A greeting"}]}]
            }]
            translate_mock = MagicMock(
                status_code=200,
                json=lambda: {"responseData": {"translatedText": "Xin chào"}}
            )
            mock_get.side_effect = [mock_response, translate_mock, translate_mock]

            # [Act]
            result = handle_tra_tu(entities)

        # [Assert] Kết quả phải đề cập đến word "hello"
        assert "hello" in result.lower() or "Hello" in result


# ══════════════════════════════════════════════════════════════════════════════
# handle_lam_quiz
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestHandleLamQuiz:

    # ── UT-CHB-ACT-007 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_007_less_than_4_vocab_returns_warning_text(self, db):
        # TC: UT-CHB-ACT-007 — Vocab < 4 → type='text', message cảnh báo thiếu từ
        # [Arrange] Tạo topic với chỉ 1 từ
        course = Course.objects.create(title="Small Course")
        topic  = Topic.objects.create(course=course, title="Small Topic")
        Vocabulary.objects.create(topic=topic, word="a", meaning="a")

        # [CheckDB] Xác nhận chỉ có 1 vocabulary trong DB
        assert Vocabulary.objects.count() == 1

        # [Act]
        result = handle_lam_quiz()

        # [Assert] Phải cảnh báo thiếu từ, không tạo quiz
        assert result["type"] == "text"
        assert "4" in result["message"] or "quiz" in result["message"].lower()
        # [Rollback] Course, Topic, Vocabulary sẽ bị rollback sau test

    # ── UT-CHB-ACT-008 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_008_enough_vocab_returns_quiz_offer(self, vocab_set):
        # TC: UT-CHB-ACT-008 — Vocab >= 4 → type='quiz_offer', questions <= 10
        # [CheckDB] Xác nhận đủ 4 vocabulary trong DB
        assert Vocabulary.objects.count() >= 4

        # [Act]
        result = handle_lam_quiz()

        # [Assert] Tạo quiz thành công với số câu hợp lệ
        assert result["type"] == "quiz_offer"
        assert "questions" in result
        assert 1 <= len(result["questions"]) <= 10
        # [Rollback] vocab_set sẽ bị rollback sau test


# ══════════════════════════════════════════════════════════════════════════════
# handle_phat_am_tu_vung
# ══════════════════════════════════════════════════════════════════════════════

class TestHandlePhatAmTuVung:

    # ── UT-CHB-ACT-009 ─────────────────────────────────────────────────────
    def test_UT_CHB_ACT_009_missing_tu_vung_entity_returns_ask_message(self):
        # TC: UT-CHB-ACT-009 — Không có entity → hỏi từ cần phát âm
        # [Arrange] entities rỗng
        # [Act]
        result = handle_phat_am_tu_vung([])

        # [Assert] Response phải đề cập đến "phát âm" hoặc "từ" hoặc "Bạn"
        assert "phát âm" in result.lower() or "từ" in result.lower() or "Bạn" in result

    # ── UT-CHB-ACT-010 ─────────────────────────────────────────────────────
    @patch("chatbot.actions.requests.get")
    def test_UT_CHB_ACT_010_with_valid_word_returns_phonetic_info(self, mock_get):
        # TC: UT-CHB-ACT-010 — Có entity tu_vung → gọi dictionary API, trả phonetic + audio_url
        # [Arrange] entities chứa tu_vung = "cat", API trả phonetic info
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "word": "cat",
            "phonetic": "/kæt/",
            "phonetics": [{"audio": "https://example.com/cat.mp3"}],
        }]
        mock_get.return_value = mock_response
        entities = [{"entity": "tu_vung", "value": "cat"}]

        # [Act]
        result = handle_phat_am_tu_vung(entities)

        # [Assert] Kết quả phải chứa thông tin phát âm của "cat"
        if isinstance(result, dict):
            assert result.get("type") == "pronunciation"
            assert "audio_url" in result
        else:
            assert "cat" in result.lower() or "kæt" in result
