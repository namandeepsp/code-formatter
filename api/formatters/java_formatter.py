import subprocess
import shutil
import os
import tempfile
import resource
from typing import Tuple
from .base import CodeFormatter, FormatterResult

class JavaFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"java"}
    
    def __init__(self):
        self.jar_path = os.getenv("JAVA_FORMATTER_PATH", "/app/google-java-format.jar")
        self.java_available = self._check_java()
        self.max_code_size = 50 * 1024  # 50KB limit for Java
        
    def _check_java(self) -> bool:
        """Verify Java and JAR are available"""
        java_exists = shutil.which("java") is not None
        jar_exists = os.path.exists(self.jar_path)
        
        if not jar_exists:
            # Try to download if missing (self-healing)
            try:
                import urllib.request
                url = "https://github.com/google/google-java-format/releases/download/v1.17.0/google-java-format-1.17.0-all-deps.jar"
                urllib.request.urlretrieve(url, self.jar_path)
                jar_exists = True
            except:
                pass
                
        return java_exists and jar_exists
    
    def _set_memory_limit(self):
        """Set memory limit for subprocess"""
        try:
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        except:
            pass  # Ignore if not supported on platform
    
    def _format_with_temp_file(self, code: str) -> Tuple[str, bool, str]:
        """Use temp file instead of stdin to avoid memory issues"""
        temp_path = None
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name
            
            # Run formatter with memory limit
            self._set_memory_limit()
            result = subprocess.run(
                ["java", "-Xmx256m", "-jar", self.jar_path, temp_path],
                capture_output=True,
                timeout=8,
                text=True
            )
            
            if result.returncode == 0:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    formatted = f.read()
                return formatted, True, None
            else:
                return code, False, result.stderr or "Formatting failed"
                
        except subprocess.TimeoutExpired:
            return code, False, "Formatting timeout (8s)"
        except Exception as e:
            return code, False, f"Error: {str(e)}"
        finally:
            # Ensure cleanup
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    def format(self, code: str) -> FormatterResult:
        # Input validation
        if not code or len(code.strip()) == 0:
            return FormatterResult(code, False, "Empty code")
        
        if len(code) > self.max_code_size:
            return FormatterResult(code, False, f"Code too large (max {self.max_code_size//1024}KB)")
        
        if not self.java_available:
            return FormatterResult(code, False, "Java formatter unavailable")
        
        # Format using temp file
        formatted, success, error = self._format_with_temp_file(code)
        return FormatterResult(formatted, success, error)
    
    def supports_language(self, language: str) -> bool:
        return language.lower() in self.SUPPORTED_LANGUAGES