from fastapi import FastAPI
from config.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"/docs",
    redoc_url=f"/redoc",
)
