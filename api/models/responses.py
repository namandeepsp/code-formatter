from pydantic import BaseModel
from typing import Optional, List


class FormatResponse(BaseModel):
    formatted_code: str
    success: bool
    error: Optional[str] = None


class LanguagesResponse(BaseModel):
    languages: List[str]


class DetectResponse(BaseModel):
    language: Optional[str]
    confidence: str
