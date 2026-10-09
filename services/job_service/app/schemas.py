from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: str | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
    salary: str | None = None
    is_active: bool | None = None


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: str | None
    recruiter_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)