import subprocess
import shutil
import tempfile
import os
from .base import CodeFormatter, FormatterResult

class GoFormatter(CodeFormatter):
    SUPPORTED_LANGUAGES = {"go"}
    
    def __init__(self):
        self.gofmt_available = shutil.which("gofmt") is not None
        self.max_code_size = 100 * 1024  # 100KB for Go
        
    def format(self, code: str) -> FormatterResult:
        if not code or len(code.strip()) == 0:
            return FormatterResult(code, False, "Empty code")
        
        if len(code) > self.max_code_size:
            return FormatterResult(code, False, f"Code too large (max {self.max_code_size//1024}KB)")
        
        if not self.gofmt_available:
            return FormatterResult(code, False, "Go formatter unavailable")
        
        # Use temp file for Go as well
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                ["gofmt", temp_path],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                return FormatterResult(result.stdout, True, None)
            else:
                error_msg = result.stderr or "Formatting failed"
                return FormatterResult(code, False, error_msg)
                
        except subprocess.TimeoutExpired:
            return FormatterResult(code, False, "Formatting timeout")
        except Exception as e:
            return FormatterResult(code, False, f"Error: {str(e)}")
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    def supports_language(self, language: str) -> bool:
        return language.lower() in self.SUPPORTED_LANGUAGES