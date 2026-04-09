from functools import lru_cache
from api.services.formatter_service import FormatterService
from api.formatters import PythonFormatter, GoFormatter, JavaFormatter

@lru_cache(maxsize=1)
def get_formatter_service() -> FormatterService:
    """Initialize formatters with proper error handling"""
    formatters = []
    
    # Python always works
    formatters.append(PythonFormatter())
    
    # Go formatter
    try:
        go_formatter = GoFormatter()
        formatters.append(go_formatter)
    except Exception as e:
        print(f"Warning: Go formatter not available: {e}")
    
    # Java formatter with memory optimizations
    try:
        java_formatter = JavaFormatter()
        formatters.append(java_formatter)
        print("Java formatter initialized with memory optimizations")
    except Exception as e:
        print(f"Warning: Java formatter init failed: {e}")
    
    return FormatterService(formatters)