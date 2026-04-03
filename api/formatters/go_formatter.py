import subprocess
import shutil
from .base import CodeFormatter, FormatterResult


class GoFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"go"}

    def __init__(self):
        self.gofmt_available = shutil.which("gofmt") is not None

    def format(self, code: str) -> FormatterResult:
        if not self.gofmt_available:
            return FormatterResult(
                code, 
                False, 
                "Go formatter not available. Install Go: sudo apt install golang-go"
            )
        
        try:
            result = subprocess.run(
                ["gofmt"],
                input=code.encode("utf-8"),
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return FormatterResult(result.stdout.decode("utf-8"), True)
            else:
                error_msg = result.stderr.decode("utf-8")
                return FormatterResult(code, False, error_msg or "Formatting failed")
        except subprocess.TimeoutExpired:
            return FormatterResult(code, False, "Formatting timeout")
        except Exception as e:
            return FormatterResult(code, False, f"Formatting error: {str(e)}")

    def supports_language(self, language: str) -> bool:
        return language.lower() in self.SUPPORTED_LANGUAGES
