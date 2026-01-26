"""
Question types modules for learning system.

Tự động đăng ký tất cả các question types khi import module này.
"""

from .registry import registry, QuestionTypeRegistry

# Import các question types (sẽ được đăng ký tự động)
from .listening import ListeningQuestionType
from .reading import ReadingQuestionType
from .writing import WritingQuestionType
from .matching import MatchingQuestionType
from .speaking import SpeakingQuestionType

# Tự động đăng ký các question types; comment/uncomment Để bật/tắt
registry.register(ListeningQuestionType)
registry.register(ReadingQuestionType)
registry.register(WritingQuestionType)
registry.register(MatchingQuestionType)
registry.register(SpeakingQuestionType)

__all__ = [
    'registry',
    'QuestionTypeRegistry',
    'ListeningQuestionType',
    'ReadingQuestionType',
    'WritingQuestionType',
    'MatchingQuestionType',
    'SpeakingQuestionType',
]

