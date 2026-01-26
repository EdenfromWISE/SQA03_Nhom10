import random
from typing import List

import requests

from vocabulary.models import Vocabulary


def handle_chao_hoi():
    """Trả lời lời chào từ người dùng."""
    return "Chào bạn, tôi có thể giúp gì cho bạn về từ vựng?"


def translate_text_to_vietnamese(text_to_translate):
    """Gọi MyMemory API để dịch văn bản sang tiếng Việt."""
    if not text_to_translate or text_to_translate == "Không tìm thấy định nghĩa.":
        return "Không có"

    api_url = f"https://api.mymemory.translated.net/get?q={text_to_translate}&langpair=en|vi"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        return response_data["responseData"].get("translatedText", text_to_translate)
    except Exception:
        return text_to_translate


def handle_tra_tu(entities):
    """Tra cứu từ vựng và trả về thông tin chi tiết."""
    word_to_lookup = None
    for entity in entities:
        if entity.get("entity") == "tu_vung":
            word_to_lookup = entity.get("value")
            break

    if not word_to_lookup:
        return "Bạn muốn tra từ nào vậy?"

    simple_vietnamese_meaning = translate_text_to_vietnamese(word_to_lookup)

    dictionary_api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_lookup}"
    try:
        response = requests.get(dictionary_api_url, timeout=10)
        if response.status_code != 200:
            return f"Rất tiếc, tôi không tìm thấy từ '{word_to_lookup}'."

        data = response.json()[0]

        word = data.get("word", word_to_lookup)
        phonetic = data.get("phonetic", "Không có")
        english_definition = "Không tìm thấy định nghĩa."

        if data.get("meanings") and data["meanings"][0].get("definitions"):
            english_definition = (
                data["meanings"][0]["definitions"][0].get(
                    "definition", "Không tìm thấy định nghĩa."
                )
            )

        detailed_vietnamese_definition = translate_text_to_vietnamese(english_definition)

        reply = (
            f"📖 Từ: {word.capitalize()}\n"
            f"🔊 Phiên âm: {phonetic}\n"
            f"🇻🇳 Nghĩa Tiếng Việt: {simple_vietnamese_meaning.capitalize()}\n"
            f"📜 Định nghĩa chi tiết: {detailed_vietnamese_definition}"
        )
        return reply

    except requests.exceptions.RequestException:
        return "Đã có lỗi xảy ra khi kết nối đến từ điển. Vui lòng thử lại sau."
    except (IndexError, KeyError):
        return f"Rất tiếc, tôi không thể phân tích dữ liệu cho từ '{word_to_lookup}'."


def handle_lam_quiz():
    """Sinh bộ câu hỏi trắc nghiệm (tối đa 10 câu) từ kho từ vựng."""

    vocabularies: List[Vocabulary] = list(Vocabulary.objects.all())
    total_vocab = len(vocabularies)

    if total_vocab < 4:
        return {
            "type": "text",
            "message": "Cần ít nhất 4 từ vựng để tạo quiz trắc nghiệm. Hãy quay lại sau nhé!",
        }

    question_count = min(10, total_vocab)
    selected_vocab = random.sample(vocabularies, question_count)

    formatted_questions = [
        _build_multiple_choice_question(vocab, vocabularies)
        for vocab in selected_vocab
    ]

    intro_message = (
        "Quiz Time! Bạn đã sẵn sàng chinh phục "
        f"{len(formatted_questions)} câu hỏi ôn luyện như trong bài kiểm tra chưa?"
    )

    return {
        "type": "quiz_offer",
        "message": intro_message,
        "questions": formatted_questions,
    }


def _build_multiple_choice_question(
    vocabulary: Vocabulary, all_vocabularies: List[Vocabulary]
) -> dict:
    distractor_pool = [v for v in all_vocabularies if v.id != vocabulary.id]
    distractor_count = min(3, len(distractor_pool))
    distractors = random.sample(distractor_pool, distractor_count)

    options = [vocabulary.word] + [item.word for item in distractors]
    random.shuffle(options)

    correct_index = options.index(vocabulary.word)

    example_parts: List[str] = []
    if vocabulary.example_en:
        example_parts.append(f"Ví dụ EN: {vocabulary.example_en}")
    if vocabulary.example_vi:
        example_parts.append(f"Ví dụ VI: {vocabulary.example_vi}")
    explanation = "\n".join(example_parts)

    return {
        "id": vocabulary.id,
        "prompt": f"Chọn từ tiếng Anh tương ứng với nghĩa: \"{vocabulary.meaning}\"",
        "meaning": vocabulary.meaning,
        "options": options,
        "answerIndex": correct_index,
        "word": vocabulary.word,
        "pronunciation": vocabulary.pronunciation,
        "explanation": explanation,
    }


def handle_hoi_chuc_nang():
    """Hàm xử lý khi người dùng hỏi về chức năng của chatbot."""
    reply = (
        "🤖 Tôi là chatbot hỗ trợ học từ vựng tiếng Anh. Tôi có thể giúp bạn:\n\n"
        "📖 <strong>Tra từ vựng</strong>: Tôi có thể tra nghĩa, phiên âm và định nghĩa chi tiết của bất kỳ từ tiếng Anh nào.\n"
        "🔊 <strong>Phát âm từ vựng</strong>: Tôi có thể hướng dẫn bạn cách phát âm các từ tiếng Anh.\n"
        "🧠 <strong>Làm Quiz</strong>: Tôi có thể tạo các câu đố từ vựng để bạn luyện tập.\n\n"
        "Hãy thử hỏi tôi bất kỳ điều gì về từ vựng nhé!"
    )
    return reply


def handle_gioi_thieu_trang_web():
    """Hàm xử lý khi người dùng hỏi về trang web."""
    reply = (
        "🌐 <strong>E-Vocab</strong> là một nền tảng học từ vựng tiếng Anh thông minh:\n\n"
        "✨ <strong>Tính năng chính</strong>:\n"
        "• Tra từ điển tiếng Anh với nghĩa tiếng Việt\n"
        "• Học phát âm chuẩn\n"
        "• Luyện tập với quiz từ vựng\n"
        "• Quản lý từ vựng cá nhân\n"
        "• Theo dõi tiến độ học tập\n\n"
        "🎯 <strong>Mục tiêu</strong>: Giúp bạn học và ghi nhớ từ vựng tiếng Anh một cách hiệu quả và thú vị!\n\n"
        "Bạn có muốn bắt đầu học từ vựng ngay không?"
    )
    return reply



def handle_phat_am_tu_vung(entities):
    """Hàm xử lý khi người dùng hỏi về cách phát âm từ vựng."""
    word_to_pronounce = None
    for entity in entities:
        if entity.get("entity") == "tu_vung":
            word_to_pronounce = entity.get("value")
            break

    if not word_to_pronounce:
        return "Bạn muốn phát âm từ nào vậy? Hãy cho tôi biết từ bạn muốn học cách đọc nhé!"

    # Lấy thông tin phát âm từ API từ điển
    dictionary_api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_pronounce}"
    try:
        response = requests.get(dictionary_api_url, timeout=10)
        if response.status_code != 200:
            return f"Rất tiếc, tôi không tìm thấy từ '{word_to_pronounce}' để phát âm."

        data = response.json()[0]
        word = data.get("word", word_to_pronounce)
        phonetic = data.get("phonetic", "Không có phiên âm")

        # Lấy audio URL nếu có
        audio_url = None
        if data.get("phonetics"):
            for phonetic_data in data["phonetics"]:
                if phonetic_data.get("audio"):
                    audio_url = phonetic_data["audio"]
                    break

        reply_text = (
            f"🔊 <strong>Cách phát âm từ: {word.capitalize()}</strong>\n\n"
            f"📝 <strong>Phiên âm</strong>: {phonetic}\n"
        )

        if audio_url:
            # Trả về dict với type và audio_url để frontend có thể tự động phát
            return {
                "type": "pronunciation",
                "message": reply_text,
                "audio_url": audio_url,
                "word": word.capitalize(),
                "phonetic": phonetic,
            }
        else:
            reply_text += "\n💡 **Gợi ý**: Bạn có thể tra từ này trên từ điển online để nghe phát âm chuẩn hơn."
            return reply_text

    except requests.exceptions.RequestException:
        return "Đã có lỗi xảy ra khi kết nối đến từ điển. Vui lòng thử lại sau."
    except (IndexError, KeyError):
        return f"Rất tiếc, tôi không thể lấy thông tin phát âm cho từ '{word_to_pronounce}'."


