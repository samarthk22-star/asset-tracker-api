from app.database import get_connection


def create_employee(employee_code, name, department):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO employees (employee_code, name, department) VALUES (?, ?, ?)",
            (employee_code, name, department)
        )
        employee_id = cursor.lastrowid
    return get_employee(employee_id)


def get_employee(employee_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, employee_code, name, department FROM employees WHERE id = ?",
            (employee_id,)
        ).fetchone()
        return dict(row) if row else None


def get_employee_assets(employee_id):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT a.id, a.asset_code, a.name, a.category
            FROM assignments x
            JOIN assets a ON a.id = x.asset_id
            WHERE x.employee_id = ? AND x.returned_at IS NULL
            ORDER BY a.id
        """, (employee_id,)).fetchall()
        return [dict(row) for row in rows]
