
from fastapi import FastAPI
from app.routes.health import router as health_router
from app.database import create_database

app = FastAPI(title="Asset Tracker API")

create_database()

app.include_router(health_router)


@app.get("/")
def home():
    return {"message": "Asset Tracker API is running"}
