
from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification Service")

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "service": "notification-service",
        "status": "healthy",
    }
