
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
                """
                INSERT INTO assignments (asset_id, employee_id)
                VALUES (?, ?)
                """,
                (asset_id, employee_id),
            )
            connection.commit()
            row = connection.execute(
                "SELECT * FROM assignments WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return dict(row)
        except sqlite3.IntegrityError:
            connection.rollback()
            return "asset_already_assigned"
    finally:
        connection.close()


def return_assignment(assignment_id):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM assignments WHERE id = ?",
            (assignment_id,),
        ).fetchone()

        if row is None:
            return "missing"

        if row["returned_at"] is not None:
            return "already_returned"

        connection.execute(
            """
            UPDATE assignments
            SET returned_at = CURRENT_TIMESTAMP
            WHERE id = ? AND returned_at IS NULL
            """,
            (assignment_id,),
        )
        connection.commit()

        updated = connection.execute(
            "SELECT * FROM assignments WHERE id = ?",
            (assignment_id,),
        ).fetchone()
        return dict(updated)
    finally:
        connection.close()


def get_asset_assignments(asset_id, limit=20, offset=0):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, asset_id, employee_id, assigned_at, returned_at
            FROM assignments
            WHERE asset_id = ?
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (asset_id, limit, offset),
        ).fetchall()
        return [dict(row) for row in rows]
