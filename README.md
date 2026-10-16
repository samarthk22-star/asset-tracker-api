# Asset Tracker API

## Overview
A REST API built with FastAPI and SQLite to manage assets, employees, and asset assignments.

## Requirements
- Python 3.12 or newer
- Git

## Setup
Clone the repository and open its folder:

```bash
git clone https://github.com/samarthk22-star/asset-tracker-api.git
cd asset-tracker-api
```

Create and activate a virtual environment.

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:
```powershell
python -m pip install -r requirements.txt
```

## Database
The SQLite database is initialized by the application. Run the application once to initialize it.

## Run the API
```powershell
python -m uvicorn main:app --reload
```

Open the interactive API documentation at:
http://127.0.0.1:8000/docs

Health check:
http://127.0.0.1:8000/health

## Run tests
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
| GET | `/employees/{employee_id}` | Retrieve an employee |
| GET | `/employees/{employee_id}/assets` | List an employee's current assets |
| POST | `/assignments` | Assign an asset to an employee |
| POST | `/assignments/{assignment_id}/return` | Return an assigned asset |

## Common errors
- `404 Not Found`: The requested resource or referenced ID does not exist.
- `409 Conflict`: Duplicate codes or an asset that is already assigned.
- `422 Unprocessable Entity`: Request data fails validation.

The interactive `/docs` page shows the request schemas and response details.
