
import re

from pydantic import BaseModel, field_validator, model_validator


class EmployeeCreate(BaseModel):
    employee_code: str
    name: str
    email: str
    department: str

    @field_validator("employee_code", "name", "email", "department")
    @classmethod
    def non_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def valid_email(cls, value):
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email address")
        return value.lower()


class EmployeeUpdate(BaseModel):
    employee_code: str | None = None
    name: str | None = None
    email: str | None = None
    department: str | None = None

    @field_validator("employee_code", "name", "email", "department")
    @classmethod
    def validate_fields(cls, value):
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def valid_email(cls, value):
        if value is not None:
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
                raise ValueError("Invalid email address")
            return value.lower()
        return value

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")

        if any(
            getattr(self, field) is None
            for field in self.model_fields_set
        ):
            raise ValueError("Updated fields cannot be null")

        return self


class EmployeeResponse(EmployeeCreate):
    id: int
