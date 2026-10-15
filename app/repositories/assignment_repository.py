import sqlite3
from app.database import get_connection


def create_assignment(asset_id, employee_id):
    connection = get_connection()
    try:
        if not connection.execute(
            "SELECT id FROM assets WHERE id = ?", (asset_id,)
        ).fetchone():
            return "asset_missing"

        if not connection.execute(
            "SELECT id FROM employees WHERE id = ?", (employee_id,)
        ).fetchone():
            return "employee_missing"

        try:
            cursor = connection.execute(
                "INSERT INTO assignments (asset_id, employee_id) VALUES (?, ?)",
                (asset_id, employee_id)
            )
            connection.commit()
            return {"id": cursor.lastrowid, "asset_id": asset_id,
                    "employee_id": employee_id}
        except sqlite3.IntegrityError:
            connection.rollback()
            return "asset_already_assigned"
    finally:
        connection.close()


def return_assignment(assignment_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM assignments WHERE id = ? AND returned_at IS NULL",
            (assignment_id,)
        ).fetchone()
        if not row:
            return False
        connection.execute(
            "UPDATE assignments SET returned_at = CURRENT_TIMESTAMP WHERE id = ?",
            (assignment_id,)
        )
        return True
