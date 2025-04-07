from sqlalchemy import Column, ForeignKey, Integer, String

from app.models.user.user import User


class Employer(User):
    __tablename__ = "employers"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    name = Column(String(100), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "employer",
    }
