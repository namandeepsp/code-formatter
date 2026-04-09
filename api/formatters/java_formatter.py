import subprocess
import shutil
import os
import tempfile
import gc
import time
from typing import Tuple, Optional
from .base import CodeFormatter, FormatterResult

class JavaFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"java"}
    
    def __init__(self):
        self.jar_path = os.getenv("JAVA_FORMATTER_PATH", "./google-java-format.jar")
        self.max_code_size = 50 * 1024  # 50KB limit for Java
        self._java_available: Optional[bool] = None
        self._download_attempted = False
        self._active_processes = 0
        self._max_concurrent = 1  # Limit concurrent Java formatting
    
    @property
    def java_available(self) -> bool:
        """Lazy check - only verify when actually needed"""
        if self._java_available is None:
            java_exists = shutil.which("java") is not None
            jar_exists = os.path.exists(self.jar_path)
            self._java_available = java_exists and jar_exists
        return self._java_available
    
    def _download_jar(self) -> bool:
        """Download JAR only when formatting is first attempted"""
        if self._download_attempted:
            return False
        
        self._download_attempted = True
        try:
            import urllib.request
            import socket
            from urllib.parse import urlparse
            
            socket.setdefaulttimeout(10)
            url = "https://github.com/google/google-java-format/releases/download/v1.17.0/google-java-format-1.17.0-all-deps.jar"
            
            # Validate URL scheme for security
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ('http', 'https'):
                raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")
            
            os.makedirs(os.path.dirname(self.jar_path), exist_ok=True)
            urllib.request.urlretrieve(url, self.jar_path)
            
            if os.path.exists(self.jar_path) and os.path.getsize(self.jar_path) > 0:
                self._java_available = True
                return True
                
        except Exception as e:
            print(f"Failed to download Java formatter: {e}")
            
        return False
    
    def _format_with_temp_file(self, code: str) -> Tuple[str, bool, str]:
        """Use temp file with aggressive memory limits for Java"""
        temp_path = None
        process = None
        
        try:
            # Wait if too many active processes (prevents memory spike)
            wait_count = 0
            while self._active_processes >= self._max_concurrent and wait_count < 10:
                time.sleep(0.5)
                wait_count += 1
            
            self._active_processes += 1
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.java', 
                                            delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name
            
            # Run with extremely tight memory limits
            cmd = [
                "java",
                "-Xmx64m",           # Max 64MB heap (was 256m)
                "-Xms16m",           # Start with 16MB
                "-XX:+UseSerialGC",  # Use serial GC (less memory)
                "-XX:MaxMetaspaceSize=32m",  # Limit metaspace
                "-XX:CompressedClassSpaceSize=16m",
                "-jar", self.jar_path,
                temp_path
            ]
            
            # Use Popen for better process control
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=8)
                
                if process.returncode == 0:
                    # google-java-format emits formatted code to stdout unless "-i" is used.
                    # Prefer stdout, but keep file-read fallback for compatibility.
                    formatted = stdout if stdout and stdout.strip() else None
                    if not formatted:
                        with open(temp_path, 'r', encoding='utf-8') as f:
                            formatted = f.read()
                    return formatted, True, None
                else:
                    return code, False, stderr or "Formatting failed"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
                return code, False, "Formatting timeout (8s)"
                
        except Exception as e:
            return code, False, f"Error: {str(e)}"
        finally:
            self._active_processes = max(0, self._active_processes - 1)
            
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            
            # Aggressive garbage collection after Java formatting
            gc.collect()
    
    def format(self, code: str) -> FormatterResult:
        # Input validation
        if not code or not code.strip():
            return FormatterResult(code, False, "Empty code")
        
        if len(code) > self.max_code_size:
            return FormatterResult(code, False, f"Code too large (max {self.max_code_size//1024}KB)")
        
        # Lazy initialization
        if not self.java_available:
            if not self._download_jar():
                return FormatterResult(code, False, "Java formatter unavailable")
        
        # Format with memory limits
        formatted, success, error = self._format_with_temp_file(code)
        return FormatterResult(formatted, success, error)
    
    def supports_language(self, language: str) -> bool:
        return language.lower() in self.SUPPORTED_LANGUAGES
