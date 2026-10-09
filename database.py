
import sqlite3

db = sqlite3.connect("asset_tracker.db")

db.execute("CREATE TABLE Assets (id INTEGER, name TEXT)")
db.execute("CREATE TABLE Employees (id INTEGER, name TEXT)")
db.execute("CREATE TABLE Assignments (asset_id INTEGER, employee_id INTEGER)")

db.close()

print("Database created")
