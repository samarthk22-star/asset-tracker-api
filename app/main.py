import json
import logging
import time
import uuid

from fastapi import FastAPI, Request

from app.database import init_db
from app.routes.asset_routes import router as asset_router
from app.routes.employee_routes import router as employee_router
from app.routes.assignment_routes import router as assignment_router


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("asset_tracker.requests")

app = FastAPI(title="Asset Tracker API")

init_db()

app.include_router(asset_router)
app.include_router(employee_router)
app.include_router(assignment_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            json.dumps({
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            })
        )


@app.get("/health")
def health_check():
    return {"status": "healthy"}