from pydantic import BaseModel, Field


class FormatRequest(BaseModel):
    code: str = Field(..., description="Source code to format")
    language: str = Field(..., description="Programming language (python, go, django, flask, fastapi, golang)")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def hello( ):\n  print('world')",
                "language": "python"
            }
        }
