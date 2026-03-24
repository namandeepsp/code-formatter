import subprocess
import shutil
import os
from .base import CodeFormatter, FormatterResult


class JavaFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"java"}

    def __init__(self):
        self.jar_path = "google-java-format.jar"
        self.java_available = shutil.which("java") is not None
        self.jar_exists = os.path.exists(self.jar_path)

    def format(self, code: str) -> FormatterResult:
        if not self.java_available:
            return FormatterResult(
                code,
                False,
                "Java not available. Install JDK: sudo apt install default-jdk"
            )
        
        if not self.jar_exists:
            return FormatterResult(
                code,
                False,
                "Google Java Format not available. Please redeploy."
            )
        
        try:
            result = subprocess.run(
                ["java", "-jar", self.jar_path, "-"],
                input=code.encode("utf-8"),
                capture_output=True,
                timeout=10
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
