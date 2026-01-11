from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # LLM
    OPENAI_API_KEY: str = ""

    # Language Settings
    DEFAULT_TARGET_LANGUAGE: str = "Spanish"  # Change this to switch all language assessments globally

    # Email - SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""
    
    # Frontend URL (for interview links in emails)
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
