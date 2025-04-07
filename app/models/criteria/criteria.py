from sqlalchemy import Column, Integer, String

from app.services.database import Base


class Criteria(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # job_id = Column(Integer, ForeignKey('jobs.id'))

    # job = relationship("Job", back_populates="criteria")
    # job = relationship("Job", back_populates="criteria")
