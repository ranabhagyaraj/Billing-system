import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./subledger.db")

    class Config:
        env_file = ".env"

settings = Settings()
