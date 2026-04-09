from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
import psutil
import time
from api.routes import format
from api.middleware.rate_limit import rate_limiter
from fastapi import HTTPException

app = FastAPI(
    title="Code Formatter API",
    description="Professional code formatting service",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global rate limit middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        await rate_limiter.check(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"success": False, "error": e.detail}
        )
    except Exception:
        # Prevent crash → important for stability tests
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Rate limiter failure"}
        )

    return await call_next(request)

# Request size limit
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")

    if content_length and int(content_length) > 1024 * 200:
        return JSONResponse(
            status_code=413,
            content={"success": False, "error": "Request too large (max 200KB)"}
        )

    return await call_next(request)

# Health check with dependency verification
@app.get("/health")
async def health_check():
    from api.dependencies import get_formatter_service
    import os
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "formatters": {}
    }
    
    try:
        service = get_formatter_service()
        languages = service.get_supported_languages()
        health_status["formatters"]["available"] = languages
        health_status["formatters"]["count"] = len(languages)
        
        # Test Python formatter
        test_result = service.format_code("def test(): pass", "python")
        health_status["formatters"]["python_working"] = test_result.success
        
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["error"] = str(e)
    
    # Check memory pressure
    if health_status["memory_usage_mb"] > 400:  # 400MB threshold
        health_status["status"] = "warning"
        health_status["warning"] = "High memory usage"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health_status)

# Lightweight ping for cron jobs
@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")

# Metrics endpoint for monitoring
@app.get("/metrics")
async def metrics():
    import os
    return {
        "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "cpu_percent": psutil.Process().cpu_percent(),
        "uptime_seconds": time.time() - app.start_time if hasattr(app, 'start_time') else 0
    }

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "Invalid request format", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error"}
    )

app.include_router(format.router)

app.start_time = time.time()