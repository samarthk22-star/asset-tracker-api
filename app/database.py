
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

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(employees)"
            ).fetchall()
        }

        if "email" not in columns:
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

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_active_assignment_asset
            ON assignments(asset_id)
            WHERE returned_at IS NULL
        """)

        connection.commit()
    finally:
        connection.close()
