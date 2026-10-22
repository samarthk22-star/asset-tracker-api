
from app.repositories import assignment_repository, asset_repository


class AssignmentNotFoundError(Exception):
    pass


class AssignmentAlreadyReturnedError(Exception):
    pass


class AssetNotFoundError(Exception):
    pass


def create_assignment(asset_id, employee_id):
    return assignment_repository.create_assignment(asset_id, employee_id)


def return_assignment(assignment_id):
    result = assignment_repository.return_assignment(assignment_id)

    if result == "missing":
        raise AssignmentNotFoundError

    if result == "already_returned":
        raise AssignmentAlreadyReturnedError

    return result


def get_asset_assignments(asset_id, limit=20, offset=0):
    if asset_repository.get_asset_by_id(asset_id) is None:
        raise AssetNotFoundError

    return assignment_repository.get_asset_assignments(
        asset_id, limit, offset
    )
