
from fastapi import FastAPI, Depends
from app.auth.api import router as auth_router
from app.core.api import analyze_router, document_router
from app.security.api import usuario_router
from config.config import settings
from core.exceptions import setup_exception_handlers
from app.auth.dependencies.dependencies_auth import get_current_user

def setup_routes(app: FastAPI):
    app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
    app.include_router(analyze_router.router, prefix="/analyze", tags=["Analyze"], dependencies=[Depends(get_current_user)])
    app.include_router(document_router.router, prefix="/document", tags=["Document"], dependencies=[Depends(get_current_user)])
    app.include_router(usuario_router.router, prefix="/usuario", tags=["Usuario"], dependencies=[Depends(get_current_user)])
    
    from app.core.api import notificacion_router
    app.include_router(notificacion_router.router, prefix="/notificaciones", tags=["Notificaciones"], dependencies=[Depends(get_current_user)])
    
    from app.core.api import trama_router
    app.include_router(trama_router.router, prefix="/tramas", tags=["Tramas"], dependencies=[Depends(get_current_user)])
    
    from app.core.api import audit_router
    app.include_router(audit_router.router, prefix="/audit", tags=["Audit"], dependencies=[Depends(get_current_user)])
    
    from core.realtime import websocket
    app.include_router(websocket.router, prefix="/documents", tags=["WebSockets"])
    setup_exception_handlers(app)
    
    @app.get("/")
    async def root():
        return {"message": f"Welcome to {settings.PROJECT_NAME}"}