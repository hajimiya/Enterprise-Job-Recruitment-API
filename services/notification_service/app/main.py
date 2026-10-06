from fastapi import FastAPI

app = FastAPI(title="Notification Service")


@app.get("/health")
def health_check():
    return {
        "service": "notification-service",
        "status": "healthy"
    }