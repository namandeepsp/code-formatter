from functools import lru_cache
from api.services.formatter_service import FormatterService
from api.formatters import PythonFormatter, GoFormatter, JavaFormatter

@lru_cache(maxsize=1)
def get_formatter_service() -> FormatterService:
    """Initialize formatters with proper error handling"""
    formatters = []
    
    # Add Python (always works)
    formatters.append(PythonFormatter())
    
    # Add Go if available
    try:
        go_formatter = GoFormatter()
        formatters.append(go_formatter)
    except Exception as e:
        print(f"Warning: Go formatter not available: {e}")
    
    # Add Java if available (with fallback)
    try:
        java_formatter = JavaFormatter()
        if java_formatter._check_java():
            formatters.append(java_formatter)
        else:
            print("Warning: Java formatter not available")
    except Exception as e:
        print(f"Warning: Java formatter init failed: {e}")
    
    return FormatterService(formatters)