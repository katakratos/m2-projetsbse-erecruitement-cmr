from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.criteria.criteria import Criteria
from app.models.job.job import Job
from app.schemas.criteria.criteria import CriteriaCreateUpdate, CriteriaResponse
from app.schemas.job.job import JobCreate, JobResponse, JobUpdate
from app.services.database import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs


@router.get("/{id}", response_model=JobResponse)
def get_job(id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{id}", response_model=JobResponse)
def update_job(id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(db_job, key, value)

    db.commit()
    db.refresh(db_job)
    return db_job


@router.delete("/{id}", response_model=JobResponse)
def delete_job(id: int, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(db_job)
    db.commit()
    return db_job


@router.post("/{job_id}/criteria", response_model=CriteriaResponse)
def create_criteria(
    job_id: int, criteria: CriteriaCreateUpdate, db: Session = Depends(get_db)
):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    new_criteria = Criteria(**criteria.dict(), job_id=job_id)
    db.add(new_criteria)
    db.commit()
    db.refresh(new_criteria)
    return new_criteria
    db.refresh(new_criteria)
    return new_criteria
