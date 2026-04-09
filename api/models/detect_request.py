from pydantic import BaseModel, Field, ConfigDict


class DetectRequest(BaseModel):
    code: str = Field(..., description="Source code to detect language")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "def hello():\n    print('world')",
            }
        }
    )
