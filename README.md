# Enterprise Job & Recruitment Management API

A microservices-based Job & Recruitment Management System built with **Python, FastAPI, PostgreSQL, SQLAlchemy, JWT Authentication, and Docker**.

The platform separates authentication, job management, applications, and notifications into independent services connected through a central API Gateway.

## Architecture

```text
                  Client / Frontend
                         |
                         v
                  API Gateway :8004
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     Auth Service    Job Service   Application Service
       :8000           :8001            :8002
                                          |
                                          v
                                  Notification Service
                                          :8003

              All services connect to PostgreSQL
```

## Microservices

| Service | Port | Responsibility |
|---|---:|---|
| API Gateway | 8004 | Central entry point for API requests |
| Auth Service | 8000 | Authentication, JWT tokens, and role-based access |
| Job Service | 8001 | Job creation, listing, searching, updating, and deletion |
| Application Service | 8002 | Job applications and application status management |
| Notification Service | 8003 | User notifications and application status alerts |
| PostgreSQL | 5433 on host | Persistent database; services connect on port 5432 inside Docker |

## Technology Stack

- **Language:** Python
- **API Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **HTTP Client:** HTTPX
- **Containerization:** Docker and Docker Compose
- **Version Control:** Git and GitHub

> Additional technologies such as Redis, Alembic, Pytest, and GitHub Actions should be documented as active project features once their implementation and configuration are verified.

## Project Structure

```text
Enterprise-Job&Recruitment-API/
│
├── services/
│   ├── api_gateway/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── auth_service/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── job_service/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── application_service/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── notification_service/
│       ├── app/
│       ├── Dockerfile
│       └── requirements.txt
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── map.txt
└── README.md
```

## Prerequisites

Install the following tools:

- Python
- Docker Desktop
- Git
- A GitHub account for repository access

Docker Desktop should be running before starting the services.

## Environment Configuration

Create a `.env` file in the project root. Configure these variables using your own secret values:

```dotenv
SECRET_KEY=your_secure_jwt_secret
INTERNAL_SERVICE_TOKEN=your_secure_internal_service_token
```

These variables are used for JWT verification and authenticated internal service communication.

**Security guidelines:**

- Never commit `.env` to GitHub.
- Keep `SECRET_KEY` consistent across services that verify JWTs.
- Keep `INTERNAL_SERVICE_TOKEN` consistent between Application Service and Notification Service.
- Use strong, randomly generated secrets.
- Do not publish passwords, access tokens, or production credentials.

The existing PostgreSQL container is named `postgres-db` and uses the Docker network `recruitment-network`.

The current Compose configuration expects that PostgreSQL container and network to exist already.

## Running the Project

Open PowerShell in the project root directory.

### 1. Validate the Compose configuration

```powershell
docker compose config --quiet
```

### 2. Build and start the microservices

```powershell
docker compose up -d --build
```

### 3. Check service status

```powershell
docker compose ps
```

### 4. View logs

```powershell
docker compose logs -f
```

To view a particular service's logs:

```powershell
docker compose logs -f api-gateway
```

### 5. Stop the microservices

```powershell
docker compose down
```

This command stops and removes the Compose-managed application containers. It does not remove the separately managed `postgres-db` container.

## API Documentation

Once the services are running, open the API Gateway's interactive documentation:

- **API Gateway Swagger UI:** http://localhost:8004/docs
- **Gateway health check:** http://localhost:8004/health

Individual service documentation may also be available at:

- Auth Service: http://localhost:8000/docs
- Job Service: http://localhost:8001/docs
- Application Service: http://localhost:8002/docs
- Notification Service: http://localhost:8003/docs

## API Gateway Routes

| Gateway route | Purpose |
|---|---|
| `/health` | Check Gateway health |
| `/auth/...` | Forward authentication requests |
| `/jobs/` | List jobs |
| `/jobs/{job_id}` | Retrieve a specific job |
| `/jobs/search` | Search jobs |
| `/applications/...` | Access application endpoints |
| `/notifications/...` | Access notification endpoints |

Protected endpoints require a valid JWT token in the request header:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

Actual access depends on the endpoint's authentication and role-based authorization rules.

## Example: Retrieve Jobs

Using PowerShell:

```powershell
Invoke-RestMethod `
    -Method GET `
    -Uri "http://localhost:8004/jobs/"
```

Retrieve a specific job:

```powershell
Invoke-RestMethod `
    -Method GET `
    -Uri "http://localhost:8004/jobs/3"
```

Check Gateway health:

```powershell
Invoke-RestMethod `
    -Method GET `
    -Uri "http://localhost:8004/health"
```

## Application Workflow

1. A user authenticates through the Auth Service.
2. The Auth Service issues a JWT token.
3. A recruiter creates and manages job listings.
4. A candidate views available jobs and submits an application.
5. Authorized recruiters manage application statuses.
6. The Application Service sends an internal request to the Notification Service when an application status changes.
7. The Notification Service stores the notification for the relevant user.

The internal notification request uses a shared service token rather than a user's JWT.

## Database Configuration

The project uses separate PostgreSQL databases for its services:

| Service | Database |
|---|---|
| Auth Service | `recruitment_db` |
| Job Service | `job_db` |
| Application Service | `application_db` |
| Notification Service | `notification_db` |

The application containers connect to PostgreSQL using the Docker network and the database container's internal port `5432`. The host port is `5433`.

## Troubleshooting

**Compose reports an empty configuration**

Check that `docker-compose.yml` contains valid YAML and run:

```powershell
docker compose config --quiet
```

**A service is not running**

```powershell
docker compose ps
docker compose logs --tail 100 api-gateway
```

Replace `api-gateway` with the affected service name when necessary.

**Gateway returns 502**

Check that the target service is running, uses the correct Docker network, and has the correct service URL configured.

**Gateway returns 404**

Verify that the Gateway route maps to the correct upstream service path.

**JWT authentication fails**

Verify the token, its expiration, the signing secret, and the user's current role. Log in again after changing a user's role so that the token contains the current role.

**Database connection fails**

Verify the `postgres-db` container, database name, credentials, network membership, and service environment variables.

## Current Project Status

- [x] Microservices structure created
- [x] Auth Service with JWT and role-based authorization
- [x] Job Service with job management endpoints
- [x] Application Service with application management
- [x] Notification Service with internal notification integration
- [x] API Gateway request forwarding
- [x] Dockerfiles for all five application services
- [x] Docker Compose configuration
- [x] Gateway health check and job-list integration verified

Further production-readiness work should include automated integration tests, database migrations, centralized logging, monitoring, secret management, and deployment configuration.

## Repository

GitHub: https://github.com/hajimiya/Enterprise-Job-Recruitment-API
