from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.services.database import Base


class CV(Base):
    __tablename__ = "cvs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(255))
