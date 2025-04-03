from sqlalchemy import Column,  Integer, String, ForeignKey
from app.services.database import Base
from sqlalchemy.orm import relationship

class Criteria(Base):
  __tablename__ = "criteria"
  
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)

  # job_id = Column(Integer, ForeignKey('jobs.id'))

  # job = relationship("Job", back_populates="criteria")