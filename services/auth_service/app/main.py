from fastapi import FastAPI

app = FastAPI(title="Auth Service")


@app.get("/health")
def health_check():
    return {
        "service": "auth-service",
        "status": "healthy"
    }