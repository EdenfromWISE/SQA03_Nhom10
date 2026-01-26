"""
Registry pattern để quản lý các question types.

Cho phép đăng ký/bỏ đăng ký question types động mà không cần sửa code core.
"""
from typing import Dict, List, Optional, Type

from .base import QuestionTypeBase


class QuestionTypeRegistry:
    """
    Registry để quản lý các question types.
    
    Tuân theo Singleton pattern và Dependency Inversion principle.
    """
    
    _instance = None
    _registry: Dict[str, Type[QuestionTypeBase]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QuestionTypeRegistry, cls).__new__(cls)
        return cls._instance
    
    def register(self, question_type_class: Type[QuestionTypeBase]) -> None:
        """
        Đăng ký một question type.
        
        Args:
            question_type_class: Class kế thừa QuestionTypeBase
            
        Raises:
            ValueError: Nếu question_type_class không hợp lệ
        """
        if not issubclass(question_type_class, QuestionTypeBase):
            raise ValueError(
                f"Class {question_type_class.__name__} phải kế thừa từ QuestionTypeBase"
            )
        
        question_type = question_type_class.QUESTION_TYPE
        if not question_type:
            raise ValueError(
                f"Class {question_type_class.__name__} phải định nghĩa QUESTION_TYPE"
            )
        
        self._registry[question_type] = question_type_class
    
    def unregister(self, question_type: str) -> None:
        """
        Bỏ đăng ký một question type.
        
        Args:
            question_type: Loại câu hỏi cần bỏ đăng ký
        """
        if question_type in self._registry:
            del self._registry[question_type]
    
    def get(self, question_type: str) -> Optional[Type[QuestionTypeBase]]:
        """
        Lấy question type class theo tên.
        
        Args:
            question_type: Loại câu hỏi
            
        Returns:
            QuestionTypeBase class hoặc None nếu không tìm thấy
        """
        return self._registry.get(question_type)
    
    def get_all(self) -> Dict[str, Type[QuestionTypeBase]]:
        """
        Lấy tất cả các question types đã đăng ký.
        
        Returns:
            Dict mapping question_type -> QuestionTypeBase class
        """
        return self._registry.copy()
    
    def get_all_types(self) -> List[str]:
        """
        Lấy danh sách tất cả các loại câu hỏi đã đăng ký.
        
        Returns:
            List các tên loại câu hỏi
        """
        return list(self._registry.keys())
    
    def get_display_names(self) -> Dict[str, str]:
        """
        Lấy mapping question_type -> display_name.
        
        Returns:
            Dict mapping question_type -> display_name
        """
        return {
            q_type: cls.DISPLAY_NAME
            for q_type, cls in self._registry.items()
        }
    
    def is_registered(self, question_type: str) -> bool:
        """
        Kiểm tra xem một question type đã được đăng ký chưa.
        
        Args:
            question_type: Loại câu hỏi
            
        Returns:
            True nếu đã đăng ký, False nếu chưa
        """
        return question_type in self._registry


# Global registry instance
registry = QuestionTypeRegistry()

