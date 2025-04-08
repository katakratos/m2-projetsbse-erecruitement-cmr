from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.services.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)  # connect_args={"check_same_thread": False}
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialise la base de données (utile uniquement en développement)."""
    print("Initialisation de la base de données...")
    Base.metadata.create_all(
        bind=engine
    )  # Crée les tables si elles n'existent pas encore
