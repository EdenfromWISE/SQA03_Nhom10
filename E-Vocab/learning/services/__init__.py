"""
Services for learning system.

Tự động đăng ký các question types khi import module này.
"""
# Import để đảm bảo các question types được đăng ký tự động
from . import question_types  # noqa: F401

__all__ = ['question_types']

