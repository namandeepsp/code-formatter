import os
from fastapi import Request, HTTPException, status


async def verify_api_key(request: Request):
    env = os.getenv("ENVIRONMENT", "development")
    
    # Skip API key check in development
    if env == "development":
        return "dev-key"
    
    api_key = request.headers.get("X-API-Key")
    valid_key = os.getenv("API_KEY")
    
    if not api_key or api_key != valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access"
        )
    return api_key
