from fastapi import FastAPI
from app.routes import router
from app.database import Base, engine
from app import models
app = FastAPI(title="Job Service")

Base.metadata.create_all(bind=engine)
app.include_router(router)
@app.get("/health")
def health_check():
    return {
        "service": "job-service",
        "status": "healthy"
    }