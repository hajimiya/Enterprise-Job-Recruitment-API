
import os
import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JobApplication
from app.schemas import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate
from app.security import get_current_user, require_candidate, require_recruiter

logger = logging.getLogger(__name__)

NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL",
    "http://notification-service:8003",
)

INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN")

router = APIRouter(prefix="/applications", tags=["Applications"])

JOB_SERVICE_URL = os.getenv(
    "JOB_SERVICE_URL",
    "http://job-service:8001",
)


def get_job(job_id: int):
    try:
        response = httpx.get(
            f"{JOB_SERVICE_URL}/jobs/{job_id}",
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Job Service is unavailable",
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Job not found")

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Could not verify job with Job Service",
        )

    return response.json()


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def apply_for_job(
    data: ApplicationCreate,
    current_user=Depends(require_candidate),
    db: Session = Depends(get_db),
):
    job = get_job(data.job_id)

    if not job.get("is_active", False):
        raise HTTPException(status_code=400, detail="Job is not active")

    existing = db.query(JobApplication).filter(
        JobApplication.job_id == data.job_id,
        JobApplication.candidate_id == current_user["user_id"],
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job",
        )

    application = JobApplication(
        job_id=data.job_id,
        candidate_id=current_user["user_id"],
        resume_url=data.resume_url,
        cover_letter=data.cover_letter,
    )

    db.add(application)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Application could not be created; check for a duplicate",
        )

    db.refresh(application)
    return application


@router.get("/my", response_model=list[ApplicationResponse])
def my_applications(
    current_user=Depends(require_candidate),
    db: Session = Depends(get_db),
):
    return (
        db.query(JobApplication)
        .filter(JobApplication.candidate_id == current_user["user_id"])
        .order_by(JobApplication.created_at.desc())
        .all()
    )


@router.get("/job/{job_id}", response_model=list[ApplicationResponse])
def applications_for_job(
    job_id: int,
    current_user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    job = get_job(job_id)

    if (
        current_user["role"] != "admin"
        and job.get("recruiter_id") != current_user["user_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only view applications for your own jobs",
        )

    return (
        db.query(JobApplication)
        .filter(JobApplication.job_id == job_id)
        .order_by(JobApplication.created_at.desc())
        .all()
    )


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    current_user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    application = (
        db.query(JobApplication)
        .filter(JobApplication.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    job = get_job(application.job_id)

    if (
        current_user["role"] != "admin"
        and job.get("recruiter_id") != current_user["user_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only update applications for your own jobs",
        )

    application.status = data.status
    db.commit()
    db.refresh(application)

    try:
        if not INTERNAL_SERVICE_TOKEN:
            logger.error("INTERNAL_SERVICE_TOKEN is not configured")
        else:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"{NOTIFICATION_SERVICE_URL}/notifications/internal",
                    headers={
                        "X-Internal-Token": INTERNAL_SERVICE_TOKEN,
                    },
                    json={
                        "user_id": application.candidate_id,
                        "title": "Application Status Updated",
                        "message": (
                            f"Your application for job ID "
                            f"{application.job_id} is now {application.status}."
                        ),
                        "notification_type": "application_status",
                    },
                )
                response.raise_for_status()
    except Exception:
        logger.exception(
            "Application status updated, but notification delivery failed"
        )

    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_application(
    application_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = (
        db.query(JobApplication)
        .filter(JobApplication.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    if (
        current_user["role"] != "admin"
        and application.candidate_id != current_user["user_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only withdraw your own application",
        )

    db.delete(application)
    db.commit()
