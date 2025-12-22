
from fastapi import FastAPI
from app.auth.api import router as auth_router
from app.core.api import analyze_router, document_router
from config.config import settings
from core.exceptions import setup_exception_handlers

def setup_routes(app: FastAPI):
    app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
    app.include_router(analyze_router.router, prefix="/analyze", tags=["Analyze"])
    app.include_router(document_router.router, prefix="/document", tags=["Document"])
    setup_exception_handlers(app)
    
    @app.get("/")
    async def root():
        return {"message": f"Welcome to {settings.PROJECT_NAME}"}