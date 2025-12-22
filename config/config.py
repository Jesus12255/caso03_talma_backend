from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Enterprise Backend"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    LLM_API_KEY: str = "df0b6c7119ed4e3a846c7c66f1c88197.Sf7w0bChqTnDqGuUQSJ8UIfd" 
    LLM_BASE_URL: str = "https://ollama.com/api" 
    LLM_MODEL_NAME: str = "qwen3-vl:235b-cloud"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
