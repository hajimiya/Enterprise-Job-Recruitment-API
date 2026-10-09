from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job
from app.schemas import JobCreate, JobUpdate, JobResponse
from app.security import get_current_user, require_recruiter

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job_data: JobCreate,
    current_user=Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    new_job = Job(
        **job_data.model_dump(),
        recruiter_id=current_user["user_id"]
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.is_active.is_(True)).all()

@router.get("/search", response_model=list[JobResponse])
def search_jobs(
    title: str | None = Query(default=None),
    company: str | None = Query(default=None),
    location: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Job).filter(Job.is_active.is_(True))

    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))

    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    return query.all()



@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return job



@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user=Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if (
        current_user["role"] != "admin"
        and job.recruiter_id != current_user["user_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own jobs"
        )

    for field, value in job_data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user=Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if (
        current_user["role"] != "admin"
        and job.recruiter_id != current_user["user_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own jobs"
        )

    db.delete(job)
    db.commit()