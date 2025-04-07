from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user.user import User


class Candidate(User):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(String(30), index=True)
    ahp_rank: Mapped[int] = mapped_column(nullable=False)
    final_score: Mapped[float] = mapped_column(nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "candidate",
    }
