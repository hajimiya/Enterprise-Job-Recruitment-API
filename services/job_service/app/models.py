from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    company = Column(String(150), nullable=False)
    location = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(String(100), nullable=True)
    recruiter_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)