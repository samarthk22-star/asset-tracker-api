
import sqlite3

def create_database():
    db = sqlite3.connect("asset_tracker.db")

    db.execute("PRAGMA foreign_keys = ON")

    db.execute("""
    CREATE TABLE IF NOT EXISTS Assets (
        id INTEGER PRIMARY KEY,
        asset_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS Assignments (
        id INTEGER PRIMARY KEY,
        asset_id INTEGER NOT NULL REFERENCES Assets(id),
        employee_id INTEGER NOT NULL REFERENCES Employees(id),
        assigned_at TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()
