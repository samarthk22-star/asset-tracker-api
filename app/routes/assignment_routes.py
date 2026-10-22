
from fastapi import APIRouter, HTTPException

from app.schemas.assignment import AssignmentCreate
from app.services import assignment_service

router = APIRouter(tags=["Assignments"])


@router.post("/assignments", status_code=201)
def assign_asset(assignment: AssignmentCreate):
    result = assignment_service.create_assignment(
        assignment.asset_id,
        assignment.employee_id,
    )

    if result == "asset_missing":
        raise HTTPException(status_code=404, detail="Asset not found")

    if result == "employee_missing":
        raise HTTPException(status_code=404, detail="Employee not found")

    if result == "asset_already_assigned":
        raise HTTPException(status_code=409, detail="Asset already assigned")

    return result


@router.post("/assignments/{assignment_id}/return")
def return_asset(assignment_id: int):
    try:
        return assignment_service.return_assignment(assignment_id)
    except assignment_service.AssignmentNotFoundError:
        raise HTTPException(status_code=404, detail="Assignment not found")
    except assignment_service.AssignmentAlreadyReturnedError:
        raise HTTPException(
            status_code=409,
            detail="Assignment has already been returned",
        )
