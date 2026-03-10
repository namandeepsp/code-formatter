import re
from black import format_str, FileMode
from isort import code as isort_code
from .base import CodeFormatter, FormatterResult


class PythonFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"python", "django", "flask", "fastapi"}

    def _extract_and_move_imports(self, code: str) -> str:
        """Extract all imports and move them to the top."""
        lines = code.split('\n')
        imports = []
        other_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                imports.append(stripped)
            elif stripped or other_lines:  # Keep empty lines after first non-empty
                other_lines.append(line)
        
        # Remove trailing empty lines from other_lines
        while other_lines and not other_lines[-1].strip():
            other_lines.pop()
        
        # Combine: imports + blank line + rest of code
        if imports and other_lines:
            return '\n'.join(imports) + '\n\n' + '\n'.join(other_lines)
        elif imports:
            return '\n'.join(imports)
        else:
            return '\n'.join(other_lines)

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
            # Move imports to top first
            reordered = self._extract_and_move_imports(code)
            # Sort imports
            sorted_code = isort_code(reordered, profile="black")
            # Then format with black
            formatted = format_str(sorted_code, mode=FileMode())
            return FormatterResult(formatted, True)
        except Exception:
            try:
                # Normalize indentation and try again
                normalized = self._normalize_code(code)
                reordered = self._extract_and_move_imports(normalized)
                sorted_code = isort_code(reordered, profile="black")
                formatted = format_str(sorted_code, mode=FileMode())
                return FormatterResult(formatted, True)
            except Exception as e:
                return FormatterResult(code, False, f"Cannot format: {str(e)}")

    def supports_language(self, language: str) -> bool:
        return language.lower() in self.SUPPORTED_LANGUAGES
