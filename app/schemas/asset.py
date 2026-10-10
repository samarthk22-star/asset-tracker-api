
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetCreate(BaseModel):
    asset_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)

    @field_validator("asset_code", "name", "category")
    @classmethod
    def reject_blank_values(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return value.strip()


class AssetUpdate(BaseModel):
    asset_code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)

    @field_validator("asset_code", "name", "category")
    @classmethod
    def reject_blank_values(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return value.strip() if value is not None else value


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_code: str
    name: str
    category: str
