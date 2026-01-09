import secrets
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enterprise Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    LLM_API_KEY: str 
    LLM_MODEL_NAME: str 
    DATABASE_URL: str
    REDIS_URL: str
    PASWORD_INICIAL: str
    
    GCS_BUCKET_NAME: str 
    GCP_PROJECT_ID: str
    GCP_CLIENT_EMAIL: str
    GCP_PRIVATE_KEY: str
    
    
    SECRET_KEY: str = secrets.token_hex(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

   
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USER: str = "pruebastalmativit@gmail.com"
    MAIL_PASSWORD: str = "rztrxmswypvqhxly"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
