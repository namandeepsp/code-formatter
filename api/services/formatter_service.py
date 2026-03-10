from typing import List
from api.formatters import CodeFormatter, FormatterResult


class FormatterService:
    def __init__(self, formatters: List[CodeFormatter]):
        self._formatters = formatters

    def format_code(self, code: str, language: str) -> FormatterResult:
        formatter = self._get_formatter(language)
        if not formatter:
            return FormatterResult(
                code, 
                False, 
                f"Unsupported language: {language}"
            )
        return formatter.format(code)

    def _get_formatter(self, language: str) -> CodeFormatter:
        for formatter in self._formatters:
            if formatter.supports_language(language):
                return formatter
        return None

    def get_supported_languages(self) -> List[str]:
        languages = []
        for formatter in self._formatters:
            if hasattr(formatter, 'SUPPORTED_LANGUAGES'):
                languages.extend(formatter.SUPPORTED_LANGUAGES)
        return sorted(languages)
