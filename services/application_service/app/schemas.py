
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    job_id: int = Field(gt=0)
    resume_url: str | None = Field(default=None, max_length=500)
    cover_letter: str | None = Field(default=None, max_length=3000)


class ApplicationStatusUpdate(BaseModel):
    status: Literal[
        "pending",
        "reviewing",
        "shortlisted",
        "rejected",
        "accepted",
    ]


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_url: str | None
    cover_letter: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
