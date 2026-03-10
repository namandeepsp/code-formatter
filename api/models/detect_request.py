from pydantic import BaseModel, Field


class DetectRequest(BaseModel):
    code: str = Field(..., description="Source code to detect language")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def hello():\n    print('world')"
            }
        }
