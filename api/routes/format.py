from fastapi import APIRouter, Depends, status, Request
from api.models.requests import FormatRequest
from api.models.detect_request import DetectRequest
from api.models.responses import (
    FormatResponse, 
    LanguagesResponse, 
    DetectResponse, 
    FormatData, 
    LanguagesData, 
    DetectData
)
from api.services.formatter_service import FormatterService
from api.services.language_detector import LanguageDetector
from api.dependencies import get_formatter_service
from api.middleware import verify_api_key
import logging
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/format", tags=["formatter"])


@router.post("", response_model=FormatResponse, status_code=status.HTTP_200_OK)
async def format_code(
    request: FormatRequest,
    req: Request,
    service: FormatterService = Depends(get_formatter_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Format source code with timeout protection.
    
    - Validates input size
    - Applies language-specific formatting
    - Returns formatted code or error message
    """
    # Log request (optional)
    logger.info(f"Format request from {req.client.host}: language={request.language}, size={len(request.code)}")
    
    try:
        # Format with timeout (runs in thread pool)
        result = service.format_code(request.code, request.language)
        
        if result.success:
            return FormatResponse(
                success=True,
                error=None,
                data=FormatData(formatted_code=result.formatted_code)
            )
        else:
            return FormatResponse(
                success=False,
                error=result.error,
                data=None
            )
    except Exception as e:
        logger.exception(f"Unexpected error formatting code: {e}")
        return FormatResponse(
            success=False,
            error="Internal server error during formatting",
            data=None
        )


@router.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages(
    service: FormatterService = Depends(get_formatter_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Get list of supported programming languages.
    
    Returns languages that have working formatters available.
    """
    try:
        languages = service.get_supported_languages()
        return LanguagesResponse(
            success=True,
            error=None,
            data=LanguagesData(languages=languages)
        )
    except Exception as e:
        logger.exception(f"Error getting languages: {e}")
        return LanguagesResponse(
            success=False,
            error="Failed to retrieve supported languages",
            data=None
        )


@router.post("/detect", response_model=DetectResponse)
async def detect_language(
    request: DetectRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Detect programming language from code snippets.
    
    Analyzes code patterns to identify the likely language.
    Returns language name and confidence level.
    """
    try:
        # Validate input
        if not request.code or len(request.code.strip()) == 0:
            return DetectResponse(
                success=False,
                error="Empty code provided",
                data=None
            )
        
        # Run detection in thread pool to avoid blocking
        detector = LanguageDetector()
        detected = await run_in_threadpool(detector.detect, request.code)
        
        return DetectResponse(
            success=True,
            error=None,
            data=DetectData(
                language=detected,
                confidence="high" if detected else "unknown"
            )
        )
    except Exception as e:
        logger.exception(f"Error detecting language: {e}")
        return DetectResponse(
            success=False,
            error="Language detection failed",
            data=None
        )


@router.get("/health", response_model=dict)
async def formatter_health(
    service: FormatterService = Depends(get_formatter_service)
):
    """
    Health check specific to formatter service.
    
    Tests each formatter with minimal valid code to verify functionality.
    """
    health_status = {
        "service": "formatter",
        "status": "healthy",
        "formatters": {}
    }
    
    # Test each formatter with minimal valid code
    test_cases = {
        "python": "def test(): pass",
        "go": "package main\nfunc main() {}",
        "java": "public class Test {}"
    }
    
    for language, test_code in test_cases.items():
        try:
            result = service.format_code(test_code, language, timeout=5)
            health_status["formatters"][language] = {
                "available": result.success,
                "error": result.error if not result.success else None
            }
        except Exception as e:
            health_status["formatters"][language] = {
                "available": False,
                "error": str(e)
            }
    
    # Determine overall status
    available_count = sum(1 for f in health_status["formatters"].values() if f["available"])
    if available_count == 0:
        health_status["status"] = "unhealthy"
    elif available_count < len(test_cases):
        health_status["status"] = "degraded"
    
    return health_status