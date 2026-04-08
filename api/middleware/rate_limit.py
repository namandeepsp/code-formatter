import time
from collections import defaultdict
from fastapi import Request, HTTPException, status

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests: defaultdict = defaultdict(list)
    
    async def check(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [req_time for req_time in self.requests[client_ip] if req_time > minute_ago]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute"
            )
        
        self.requests[client_ip].append(now)
        return True

# Global instance
rate_limiter = RateLimiter(requests_per_minute=30)