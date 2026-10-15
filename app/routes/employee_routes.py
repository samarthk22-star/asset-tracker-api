from fastapi import APIRouter, HTTPException
import sqlite3

from app.schemas.employee import EmployeeCreate
from app.repositories.employee_repository import (
    create_employee, get_employee, get_employee_assets
)

router = APIRouter(tags=["Employees"])


@router.post("/employees", status_code=201)
def add_employee(employee: EmployeeCreate):
    try:
        return create_employee(
            employee.employee_code, employee.name, employee.department
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Employee code already exists")


@router.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    employee = get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.get("/employees/{employee_id}/assets")
def read_employee_assets(employee_id: int):
    if not get_employee(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return get_employee_assets(employee_id)
