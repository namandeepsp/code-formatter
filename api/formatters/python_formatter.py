import re
from black import format_str, FileMode
from .base import CodeFormatter, FormatterResult


class PythonFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"python", "django", "flask", "fastapi"}

    def _normalize_code(self, code: str) -> str:
        """Fix malformed indentation by removing all leading whitespace."""
        lines = code.split('\n')
        normalized = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                normalized.append(stripped)
            else:
                normalized.append('')
        return '\n'.join(normalized)

    def format(self, code: str) -> FormatterResult:
        try:
            formatted = format_str(code, mode=FileMode())
            return FormatterResult(formatted, True)
        except Exception:
            try:
                # Normalize indentation and try again
                normalized = self._normalize_code(code)
                formatted = format_str(normalized, mode=FileMode())
                return FormatterResult(formatted, True)
            except Exception as e:
                return FormatterResult(code, False, f"Cannot format: {str(e)}")

    def supports_language(self, language: str) -> bool:
        return language.lower() in self.SUPPORTED_LANGUAGES
