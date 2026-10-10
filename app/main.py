
from fastapi import FastAPI

from app.database import init_db
from app.routes.asset_routes import router as asset_router

app = FastAPI(title="Asset Tracker API")

init_db()
app.include_router(asset_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
