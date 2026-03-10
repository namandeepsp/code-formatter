from abc import ABC, abstractmethod
from typing import Optional


class FormatterResult:
    def __init__(self, formatted_code: str, success: bool, error: Optional[str] = None):
        self.formatted_code = formatted_code
        self.success = success
        self.error = error


class CodeFormatter(ABC):
    @abstractmethod
    def format(self, code: str) -> FormatterResult:
        pass

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        pass
