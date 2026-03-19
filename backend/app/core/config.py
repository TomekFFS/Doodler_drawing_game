# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Multiplayer Platform"
    debug: bool = True

settings = Settings()