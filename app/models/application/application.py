from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import  relationship
from app.models.base import Base


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))
    cv_id = Column(Integer, ForeignKey('cvs.id'))

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    cv = relationship("CV", back_populates="application")