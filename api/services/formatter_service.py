from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from api.formatters import CodeFormatter, FormatterResult
import os
import gc


class FormatterService:
    def __init__(self, formatters: List[CodeFormatter]):
        self._formatters = formatters

        # Slightly higher for concurrency tests
        max_workers = 4
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        self._default_timeout = int(os.getenv("FORMATTER_TIMEOUT", "10"))

    def format_code(self, code: str, language: str, timeout: Optional[int] = None) -> FormatterResult:
        formatter = self._get_formatter(language)
        if not formatter:
            return FormatterResult(code, False, f"Unsupported language: {language}")

        timeout = timeout or self._default_timeout

        try:
            future = self._executor.submit(formatter.format, code)
            result = future.result(timeout=timeout)

            gc.collect()
            return result

        except FutureTimeoutError:
            return FormatterResult(code, False, f"Formatting timeout after {timeout}s")

        except Exception as e:
            return FormatterResult(code, False, f"Formatting error: {str(e)}")

    def _get_formatter(self, language: str) -> Optional[CodeFormatter]:
        language_lower = language.lower()
        for formatter in self._formatters:
            if formatter.supports_language(language_lower):
                return formatter
        return None

    def get_supported_languages(self) -> List[str]:
        base_languages = set()
        for formatter in self._formatters:
            base_languages.update(formatter.SUPPORTED_LANGUAGES)
        return sorted(list(base_languages))

    def __del__(self):
        if hasattr(self, "_executor"):
            try:
                self._executor.shutdown(wait=True)
            except:
                pass