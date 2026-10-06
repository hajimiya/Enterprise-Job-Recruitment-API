from fastapi import FastAPI

app = FastAPI(title="Application Service")


@app.get("/health")
def health_check():
    return {
        "service": "application-service",
        "status": "healthy"
    }