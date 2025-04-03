from sqlalchemy import ForeignKey, String, Integer, Column, Text
from sqlalchemy.orm import relationship
from app.models.criteria.criteria import Criteria
from app.models.employer.employer import Employer
from app.services.database import Base




class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    title = Column(String, index=True)
    # employer_id = Column(Integer, ForeignKey('employers.id'))
    nb_places = Column(Integer)
    company = Column(String, index=True)
    location = Column(String, index=True)
    type = Column(String, index=True)
    experience = Column(String, index=True)
    salary = Column(String, index=True)
    deadline = Column(String, index=True)
    requirements = Column(Text, index=True)
    skills = Column(Text, index=True)

    # criteria = relationship(Criteria, back_populates="jobs")
    # employer = relationship(Employer, back_populates="jobs")
