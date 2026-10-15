from pydantic import BaseModel, field_validator


class EmployeeCreate(BaseModel):
    employee_code: str
    name: str
    department: str

    @field_validator("employee_code", "name", "department")
    @classmethod
    def non_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


class EmployeeResponse(EmployeeCreate):
    id: int
