
import os

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response


app = FastAPI(
    title="Enterprise Job Recruitment API Gateway",
    description="Central gateway for all recruitment microservices",
    version="1.0.0",
)


# --------------------------------------------------
# MICROSERVICE URLS
# --------------------------------------------------

SERVICE_URLS = {
    "auth": os.getenv(
        "AUTH_SERVICE_URL",
        "http://auth-service:8000",
    ),
    "jobs": os.getenv(
        "JOB_SERVICE_URL",
        "http://job-service:8001",
    ),
    "applications": os.getenv(
        "APPLICATION_SERVICE_URL",
        "http://application-service:8002",
    ),
    "notifications": os.getenv(
        "NOTIFICATION_SERVICE_URL",
        "http://notification-service:8003",
    ),
}


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "service": "api-gateway",
        "status": "healthy",
        "routes": list(SERVICE_URLS.keys()),
    }


# --------------------------------------------------
# COMMON REQUEST FORWARDING FUNCTION
# --------------------------------------------------

async def forward_request(
    service_name: str,
    path: str,
    request: Request,
):
    base_url = SERVICE_URLS[service_name].rstrip("/")

    # Preserve the upstream service's complete API path.
    url = f"{base_url}/{path.lstrip('/')}"

    if request.url.query:
        url = f"{url}?{request.url.query}"

    # Forward only the necessary request headers.
    headers = {}

    for name in ("authorization", "content-type"):
        value = request.headers.get(name)
        if value:
            headers[name] = value

    body = await request.body()

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0),
            follow_redirects=True,
        ) as client:
            upstream = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )

        # Preserve the upstream response content and status.
        response_headers = {}

        for name in ("content-type",):
            value = upstream.headers.get(name)
            if value:
                response_headers[name] = value

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=response_headers,
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"{service_name} service timed out",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail=f"{service_name} service is unavailable",
        )


# --------------------------------------------------
# AUTH SERVICE
# Gateway: /auth/... -> Auth Service: /auth/...
# --------------------------------------------------

@app.api_route(
    "/auth",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def auth_root(request: Request):
    return await forward_request(
        "auth",
        "auth",
        request,
    )


@app.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def auth_path(path: str, request: Request):
    return await forward_request(
        "auth",
        f"auth/{path}",
        request,
    )


# --------------------------------------------------
# JOB SERVICE
# Gateway: /jobs/... -> Job Service: /jobs/...
# --------------------------------------------------

@app.api_route(
    "/jobs",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def jobs_root(request: Request):
    return await forward_request(
        "jobs",
        "jobs",
        request,
    )


@app.api_route(
    "/jobs/",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def jobs_root_slash(request: Request):
    return await forward_request(
        "jobs",
        "jobs/",
        request,
    )


@app.api_route(
    "/jobs/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def jobs_path(path: str, request: Request):
    return await forward_request(
        "jobs",
        f"jobs/{path}",
        request,
    )


# --------------------------------------------------
# APPLICATION SERVICE
# Gateway: /applications/... -> Application Service
# --------------------------------------------------

@app.api_route(
    "/applications",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def applications_root(request: Request):
    return await forward_request(
        "applications",
        "applications",
        request,
    )


@app.api_route(
    "/applications/",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def applications_root_slash(request: Request):
    return await forward_request(
        "applications",
        "applications/",
        request,
    )


@app.api_route(
    "/applications/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def applications_path(path: str, request: Request):
    return await forward_request(
        "applications",
        f"applications/{path}",
        request,
    )


# --------------------------------------------------
# NOTIFICATION SERVICE
# Gateway: /notifications/... -> Notification Service
# --------------------------------------------------

@app.api_route(
    "/notifications",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def notifications_root(request: Request):
    return await forward_request(
        "notifications",
        "notifications",
        request,
    )


@app.api_route(
    "/notifications/",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def notifications_root_slash(request: Request):
    return await forward_request(
        "notifications",
        "notifications/",
        request,
    )


@app.api_route(
    "/notifications/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def notifications_path(path: str, request: Request):
    return await forward_request(
        "notifications",
        f"notifications/{path}",
        request,
    )
