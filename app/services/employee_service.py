
import sqlite3

from app.repositories import employee_repository


class EmployeeNotFoundError(Exception):
    pass


class DuplicateEmployeeError(Exception):
    pass


class EmployeeAssignedError(Exception):
    pass


def create_employee(data):
    if employee_repository.get_employee_by_email(data["email"]):
        raise DuplicateEmployeeError

    try:
        return employee_repository.create_employee(
            data["employee_code"],
            data["name"],
            data["email"],
            data["department"],
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateEmployeeError from exc


def get_all_employees(limit=20, offset=0):
    return employee_repository.list_employees(limit, offset)


def get_employee(employee_id):
    employee = employee_repository.get_employee(employee_id)

    if employee is None:
        raise EmployeeNotFoundError

    return employee


def update_employee(employee_id, data):
    get_employee(employee_id)

    cleaned_data = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in data.items()
        if value is not None
    }

    if (
        "email" in cleaned_data
        and employee_repository.get_employee_by_email(
            cleaned_data["email"],
            exclude_id=employee_id,
        )
    ):
        raise DuplicateEmployeeError

    try:
        return employee_repository.update_employee(
            employee_id, cleaned_data
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateEmployeeError from exc


def delete_employee(employee_id):
    get_employee(employee_id)

    # Do not delete an employee who currently holds an asset.
    if employee_repository.get_employee_assets(employee_id):
        raise EmployeeAssignedError

    try:
        return employee_repository.delete_employee(employee_id)
    except sqlite3.IntegrityError as exc:
        # Preserve assignment history and its foreign-key references.
        raise EmployeeAssignedError from exc


def get_employee_assets(employee_id):
    get_employee(employee_id)
    return employee_repository.get_employee_assets(employee_id)
