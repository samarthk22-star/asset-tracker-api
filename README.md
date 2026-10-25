
# Asset Tracker API

## Overview

A REST API built with FastAPI and SQLite to manage assets, employees, and asset assignments. It supports asset and employee management, assignment returns, and assignment history.

## Requirements

- Python 3.12 or newer
- Git
- Locust for load testing

## Setup

Clone the repository and open its folder:

```powershell
git clone https://github.com/samarthk22-star/asset-tracker-api.git
cd asset-tracker-api
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install project dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install Locust for load testing:

```powershell
python -m pip install locust
```

## Database

The application uses SQLite. The database is initialized by the application when it starts.

Start the application to initialize the database:

```powershell
python -m uvicorn app.main:app --reload
```

The database file `asset_tracker.db` is generated locally and should not be committed to Git.

For a fresh database, stop the application and remove the generated database file before restarting. Do this only if you do not need the existing local data.

Database schema changes should be applied through the project's initialization and migration logic.

## Run the API

From the project root, run:

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## Run tests

Run the test suite:

```powershell
python -m pytest -v
```

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/assets` | Create an asset |
| GET | `/assets` | List assets |
| GET | `/assets/{asset_id}` | Retrieve an asset |
| PATCH | `/assets/{asset_id}` | Update an asset |
| DELETE | `/assets/{asset_id}` | Delete an unassigned asset |
| POST | `/employees` | Create an employee |
| GET | `/employees` | List employees |
| GET | `/employees/{employee_id}` | Retrieve an employee |
| PATCH | `/employees/{employee_id}` | Update an employee |
| DELETE | `/employees/{employee_id}` | Delete an employee, subject to API constraints |
| GET | `/employees/{employee_id}/assets` | List an employee's current assets |
| POST | `/assignments` | Assign an asset to an employee |
| POST | `/assignments/{assignment_id}/return` | Return an assigned asset |
| GET | `/assignments` | List assignment records |

Consult `/docs` for the exact request schemas, supported query parameters, and available history endpoints.

## Request logging

The API writes structured JSON request logs containing:

- Request ID
- HTTP method
- Request path
- Response status code
- Request duration in milliseconds

Request bodies and employee details are not intentionally included in these logs.

## Load testing

The load tests use Locust and request the first 100 assets:

`GET /assets?limit=100&offset=0`

Install Locust:

```powershell
python -m pip install locust
```

Start the API in one terminal:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, activate the virtual environment, change to the project root, and run the 10-user test:

```powershell
python -m locust -f locustfile.py --headless -H http://127.0.0.1:8000 -u 10 -r 2 -t 60s --csv results_10_users --csv-full-history
```

Run the 50-user test:

```powershell
python -m locust -f locustfile.py --headless -H http://127.0.0.1:8000 -u 50 -r 5 -t 60s --csv results_50_users --csv-full-history
```

The seed script can add synthetic assets for testing:

```powershell
python -m scripts.seed_load_test_data
```

The script skips duplicate asset codes but can add additional records when run again. Check the dataset size before repeating it.

Measured results, test environment, commands, and limitations are documented in `docs/performance-report.md`. Results describe the local development machine and are not production benchmarks.

Generated Locust CSV files and the local SQLite database should not be committed.

## Common errors

- `404 Not Found`: The requested resource or referenced ID does not exist.
- `409 Conflict`: Duplicate codes or an asset that is already assigned.
- `422 Unprocessable Entity`: Request data fails validation.
