from fastapi import APIRouter, HTTPException

from app.schemas.assignment import AssignmentCreate
from app.repositories.assignment_repository import (
    create_assignment, return_assignment
)

router = APIRouter(tags=["Assignments"])


@router.post("/assignments", status_code=201)
def assign_asset(assignment: AssignmentCreate):
    result = create_assignment(assignment.asset_id, assignment.employee_id)

    if result == "asset_missing":
        raise HTTPException(status_code=404, detail="Asset not found")
    if result == "employee_missing":
        raise HTTPException(status_code=404, detail="Employee not found")
    if result == "asset_already_assigned":
        raise HTTPException(status_code=409, detail="Asset already assigned")

    return result


@router.post("/assignments/{assignment_id}/return")
def return_asset(assignment_id: int):
    if not return_assignment(assignment_id):
        raise HTTPException(
            status_code=404, detail="Active assignment not found"
        )
    return {"message": "Asset returned successfully"}
