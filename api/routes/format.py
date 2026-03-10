from fastapi import APIRouter, Depends, status
from api.models.requests import FormatRequest
from api.models.detect_request import DetectRequest
from api.models.responses import FormatResponse, LanguagesResponse, DetectResponse
from api.services.formatter_service import FormatterService
from api.services.language_detector import LanguageDetector
from api.dependencies import get_formatter_service

router = APIRouter(prefix="/api/format", tags=["formatter"])


@router.post("", response_model=FormatResponse, status_code=status.HTTP_200_OK)
async def format_code(
    request: FormatRequest,
    service: FormatterService = Depends(get_formatter_service)
):
    result = service.format_code(request.code, request.language)
    return FormatResponse(
        formatted_code=result.formatted_code,
        success=result.success,
        error=result.error
    )


@router.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages(
    service: FormatterService = Depends(get_formatter_service)
):
    return LanguagesResponse(languages=service.get_supported_languages())


@router.post("/detect", response_model=DetectResponse)
async def detect_language(request: DetectRequest):
    detector = LanguageDetector()
    detected = detector.detect(request.code)
    return DetectResponse(
        language=detected,
        confidence="high" if detected else "unknown"
    )
