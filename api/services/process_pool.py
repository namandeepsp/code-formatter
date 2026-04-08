import asyncio
import subprocess
import tempfile
import os
from typing import Optional, Dict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import atexit
import resource
import signal

class FormatterProcessPool:
    """Manages subprocesses with proper cleanup and resource limits"""
    
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_processes: Dict[int, subprocess.Popen] = {}
        atexit.register(self.cleanup)
        
    def cleanup(self):
        """Force kill all orphaned subprocesses"""
        for pid, process in self.active_processes.items():
            try:
                os.kill(pid, signal.SIGKILL)
            except:
                pass
        self.executor.shutdown(wait=True)
    
    async def run_with_timeout(self, func, timeout: int = 10, *args, **kwargs):
        """Run function with timeout and resource limits"""
        loop = asyncio.get_event_loop()
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, func, *args, **kwargs),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return {"success": False, "error": "Operation timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
formatter_pool = FormatterProcessPool(max_workers=2)