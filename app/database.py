
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "asset_tracker.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_connection()

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT
            );

            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                returned_at TEXT,
                FOREIGN KEY (asset_id) REFERENCES assets(id),
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
        """)

        # Ensure the employee email column exists.
        employee_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(employees)"
            ).fetchall()
        }

        if "email" not in employee_columns:
            connection.execute(
                "ALTER TABLE employees ADD COLUMN email TEXT"
            )

        connection.execute("""
            UPDATE employees
            SET email = 'legacy-' || id || '@example.invalid'
            WHERE email IS NULL OR TRIM(email) = ''
        """)

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_email
            ON employees(email)
        """)

        # Migrate existing assignments tables.
        assignment_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(assignments)"
            ).fetchall()
        }

        if "returned_at" not in assignment_columns:
            connection.execute(
                "ALTER TABLE assignments ADD COLUMN returned_at TEXT"
            )

        # Remove the old restriction allowing only one assignment
        # per asset across its entire history.
        indexes = connection.execute(
            "PRAGMA index_list(assignments)"
        ).fetchall()

        rebuild_required = False

        for index in indexes:
            if not index["unique"] or index["partial"]:
                continue

            index_columns = connection.execute(
                f'PRAGMA index_info("{index["name"]}")'
            ).fetchall()

            column_names = [row["name"] for row in index_columns]

            if column_names == ["asset_id"]:
                rebuild_required = True
                break

        if rebuild_required:
            connection.execute("""
                CREATE TABLE assignments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    returned_at TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets(id),
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                )
            """)

            connection.execute("""
                INSERT INTO assignments_new
                    (id, asset_id, employee_id, assigned_at, returned_at)
                SELECT id, asset_id, employee_id, assigned_at, returned_at
                FROM assignments
            """)

            connection.execute("DROP TABLE assignments")

            connection.execute("""
                ALTER TABLE assignments_new RENAME TO assignments
            """)

        # An asset can have only one active assignment at a time.
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_active_assignment_asset
            ON assignments(asset_id)
            WHERE returned_at IS NULL
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
