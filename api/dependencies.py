from functools import lru_cache
from api.services.formatter_service import FormatterService
from api.formatters import PythonFormatter, GoFormatter


@lru_cache()
def get_formatter_service() -> FormatterService:
    formatters = [
        PythonFormatter(),
        GoFormatter()
    ]
    return FormatterService(formatters)
