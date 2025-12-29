import secrets
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enterprise Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://tuticket.vip",
        "https://www.tuticket.vip",
        "https://webapi.tuticket.lat",
        "https://portalapi.tuticket.lat",
        "https://tuticket.lat",
        "https://api.payzen.lat",
        "https://static.payzen.lat",
        "https://payzen.io/",
        "http://localhost:8080",
        "https://secure.payzen.lat"
    ]
    LOG_LEVEL: str = "INFO"

    LLM_API_KEY: str 
    LLM_BASE_URL: str
    LLM_MODEL_NAME: str 
    DATABASE_URL: str
    PASWORD_INICIAL: str
    
    
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
