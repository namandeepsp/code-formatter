from pydantic import BaseModel
from typing import Optional, List, Any


class FormatData(BaseModel):
    formatted_code: str


class LanguagesData(BaseModel):
    languages: List[str]


class DetectData(BaseModel):
    language: Optional[str]
    confidence: str


class ApiResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    data: Optional[Any] = None


class FormatResponse(ApiResponse):
    data: Optional[FormatData] = None


class LanguagesResponse(ApiResponse):
    data: Optional[LanguagesData] = None


class DetectResponse(ApiResponse):
    data: Optional[DetectData] = None
