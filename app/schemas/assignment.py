from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    asset_id: int = Field(gt=0)
    employee_id: int = Field(gt=0)
