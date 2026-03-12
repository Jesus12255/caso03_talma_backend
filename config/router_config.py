
from fastapi import FastAPI, Depends
from app.auth.api import router as auth_router
from app.core.api import analyze_router, document_router, dashboard_router
from app.security.api import usuario_router
from config.config import settings
from core.exceptions import setup_exception_handlers
from app.auth.dependencies.dependencies_auth import get_current_user
from app.core.api import notificacion_router
from app.core.api import trama_router
from app.core.api import audit_router
from app.core.api import irregularidad_router
from core.realtime import websocket
from app.core.websockets.copilot import router as copilot_router

def setup_routes(app: FastAPI):
    app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
    app.include_router(analyze_router.router, prefix=f"{settings.API_V1_STR}/analyze", tags=["Analyze"], dependencies=[Depends(get_current_user)])
    app.include_router(document_router.router, prefix=f"{settings.API_V1_STR}/document", tags=["Document"], dependencies=[Depends(get_current_user)])
    app.include_router(usuario_router.router, prefix=f"{settings.API_V1_STR}/usuario", tags=["Usuario"], dependencies=[Depends(get_current_user)])
    app.include_router(notificacion_router.router, prefix=f"{settings.API_V1_STR}/notificaciones", tags=["Notificaciones"], dependencies=[Depends(get_current_user)])
    app.include_router(trama_router.router, prefix=f"{settings.API_V1_STR}/tramas", tags=["Tramas"], dependencies=[Depends(get_current_user)])
    app.include_router(audit_router.router, prefix=f"{settings.API_V1_STR}/audit", tags=["Audit"], dependencies=[Depends(get_current_user)])
    app.include_router(irregularidad_router.router, prefix=f"{settings.API_V1_STR}/irregularidad", tags=["Irregularidad"], dependencies=[Depends(get_current_user)])
    app.include_router(dashboard_router.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])
    app.include_router(websocket.router, prefix="/documents", tags=["WebSockets"])
    app.include_router(copilot_router.router, tags=["Copilot WebSocket"])
    setup_exception_handlers(app)
    @app.get("/")
    async def root():
        return {"message": f"Welcome to {settings.PROJECT_NAME}"}