
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "candidate_id",
            name="uq_job_candidate_application",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, nullable=False, index=True)
    candidate_id = Column(Integer, nullable=False, index=True)

    resume_url = Column(String(500), nullable=True)
    cover_letter = Column(String(3000), nullable=True)

    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
