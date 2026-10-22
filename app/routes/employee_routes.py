
import sqlite3

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.repositories.employee_repository import (
    create_employee,
    get_employee,
    get_employee_by_email,
    list_employees,
    update_employee,
    delete_employee,
    get_employee_assets,
)

router = APIRouter(tags=["Employees"])


@router.post("/employees", status_code=status.HTTP_201_CREATED)
def add_employee(employee: EmployeeCreate):
    if get_employee_by_email(employee.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        return create_employee(
            employee.employee_code,
            employee.name,
            employee.email,
            employee.department,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Employee code or email already exists",
        )


@router.get("/employees")
def read_employees(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return list_employees(limit, offset)


@router.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    employee = get_employee(employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.patch("/employees/{employee_id}")
def edit_employee(employee_id: int, employee: EmployeeUpdate):
    if not get_employee(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    fields = employee.model_dump(exclude_unset=True)

    if "email" in fields and get_employee_by_email(
        fields["email"], exclude_id=employee_id
    ):
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        return update_employee(employee_id, fields)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Employee code or email already exists",
        )


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_employee(employee_id: int):
    if not get_employee(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    try:
        deleted = delete_employee(employee_id)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete an employee referenced by assignments",
        )

    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/employees/{employee_id}/assets")
def read_employee_assets(employee_id: int):
    if not get_employee(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    return get_employee_assets(employee_id)
