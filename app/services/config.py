from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str
    DEBUG: bool = False

    class Config:
        env_file=".env"

settings = Settings()
