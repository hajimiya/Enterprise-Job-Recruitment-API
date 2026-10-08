from .database import Base, engine
from . import models
from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Auth Service")

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "service": "auth-service",
        "status": "healthy"
    }