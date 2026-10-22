
from app.database import get_connection


def create_employee(employee_code, name, email, department):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO employees
                (employee_code, name, email, department)
            VALUES (?, ?, ?, ?)
            """,
            (employee_code, name, email, department),
        )
        employee_id = cursor.lastrowid

    return get_employee(employee_id)


def get_employee(employee_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, employee_code, name, email, department
            FROM employees
            WHERE id = ?
            """,
            (employee_id,),
        ).fetchone()

        return dict(row) if row else None


def get_employee_by_email(email, exclude_id=None):
    with get_connection() as connection:
        if exclude_id is None:
            row = connection.execute(
                "SELECT id FROM employees WHERE email = ?",
                (email,),
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT id FROM employees
                WHERE email = ? AND id != ?
                """,
                (email, exclude_id),
            ).fetchone()

        return row is not None


def list_employees(limit=20, offset=0):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, employee_code, name, email, department
            FROM employees
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

        return [dict(row) for row in rows]


def update_employee(employee_id, fields):
    if not fields:
        return get_employee(employee_id)

    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [employee_id]

    with get_connection() as connection:
        connection.execute(
            f"UPDATE employees SET {columns} WHERE id = ?",
            values,
        )

    return get_employee(employee_id)


def delete_employee(employee_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM employees WHERE id = ?",
            (employee_id,),
        )
        return cursor.rowcount > 0


def get_employee_assets(employee_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT a.id, a.asset_code, a.name, a.category
            FROM assignments x
            JOIN assets a ON a.id = x.asset_id
            WHERE x.employee_id = ?
              AND x.returned_at IS NULL
            ORDER BY a.id
            """,
            (employee_id,),
        ).fetchall()

        return [dict(row) for row in rows]