import secrets
from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enterprise Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> str | List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    LLM_API_KEY: str 
    LLM_MODEL_NAME: str 
    COPILOT_LLM_MODEL_NAME: str 
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_TASK_QUEUE: str = "document_queue"
    PASWORD_INICIAL: str
    
    GCS_BUCKET_NAME: str 
    GCP_PROJECT_ID: str
    GCP_CLIENT_EMAIL: str
    GCP_PRIVATE_KEY: str
    
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    RECAPTCHA_SECRET_KEY: str | None = None

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
