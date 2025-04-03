from sqlalchemy import Column, Integer, VARCHAR, String
from app.services.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(VARCHAR(100), unique=True, index=True)
    password_hash = Column(String(100))

    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }
    
  