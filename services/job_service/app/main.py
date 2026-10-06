from fastapi import FastAPI

app = FastAPI(title="Job Service")


@app.get("/health")
def health_check():
    return {
        "service": "job-service",
        "status": "healthy"
    }