from fastapi import APIRouter, Depends, status
from api.models.requests import FormatRequest
from api.models.detect_request import DetectRequest
from api.models.responses import FormatResponse, LanguagesResponse, DetectResponse, FormatData, LanguagesData, DetectData
from api.services.formatter_service import FormatterService
from api.services.language_detector import LanguageDetector
from api.dependencies import get_formatter_service
from api.middleware import verify_api_key

router = APIRouter(prefix="/api/format", tags=["formatter"])


@router.post("", response_model=FormatResponse, status_code=status.HTTP_200_OK)
async def format_code(
    request: FormatRequest,
    service: FormatterService = Depends(get_formatter_service),
    api_key: str = Depends(verify_api_key)
):
    result = service.format_code(request.code, request.language)
    return FormatResponse(
        success=result.success,
        error=result.error,
        data=FormatData(formatted_code=result.formatted_code)
    )


@router.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages(
    service: FormatterService = Depends(get_formatter_service),
    api_key: str = Depends(verify_api_key)
):
    try:
        languages = service.get_supported_languages()
        return LanguagesResponse(
            success=True,
            error=None,
            data=LanguagesData(languages=languages)
        )
    except Exception as e:
        return LanguagesResponse(
            success=False,
            error=str(e),
            data=None
        )


@router.post("/detect", response_model=DetectResponse)
async def detect_language(
    request: DetectRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        detector = LanguageDetector()
        detected = detector.detect(request.code)
        return DetectResponse(
            success=True,
            error=None,
            data=DetectData(
                language=detected,
                confidence="high" if detected else "unknown"
            )
        )
    except Exception as e:
        return DetectResponse(
            success=False,
            error=str(e),
            data=None
        )
