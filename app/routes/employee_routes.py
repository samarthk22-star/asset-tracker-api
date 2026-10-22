
from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services import employee_service

router = APIRouter(tags=["Employees"])


@router.post("/employees", status_code=status.HTTP_201_CREATED)
def add_employee(employee: EmployeeCreate):
    try:
        return employee_service.create_employee(employee.model_dump())
    except employee_service.DuplicateEmployeeError:
        raise HTTPException(
            status_code=409,
            detail="Employee code or email already exists",
        )


@router.get("/employees")
def read_employees(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return employee_service.get_all_employees(limit, offset)


@router.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    try:
        return employee_service.get_employee(employee_id)
    except employee_service.EmployeeNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )


@router.patch("/employees/{employee_id}")
def edit_employee(employee_id: int, employee: EmployeeUpdate):
    fields = employee.model_dump(exclude_unset=True)

    try:
        return employee_service.update_employee(employee_id, fields)
    except employee_service.EmployeeNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
    except employee_service.DuplicateEmployeeError:
        raise HTTPException(
            status_code=409,
            detail="Employee code or email already exists",
        )


@router.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_employee(employee_id: int):
    try:
        employee_service.delete_employee(employee_id)
    except employee_service.EmployeeNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
    except employee_service.EmployeeAssignedError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete an employee with assigned assets or assignment history",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/employees/{employee_id}/assets")
def read_employee_assets(employee_id: int):
    try:
        return employee_service.get_employee_assets(employee_id)
    except employee_service.EmployeeNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
