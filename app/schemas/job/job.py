from typing import List

from pydantic import BaseModel

from app.schemas.criteria.criteria import CriteriaResponse


class JobBase(BaseModel):
    title: str
    company: str
    location: str
    type: str
    experience: str
    salary: str
    deadline: str
    description: str
    requirements: str
    skills: str


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    criteria: List[CriteriaResponse] = []

    class Config:
        from_attributes = True  # remplace orm_mode
