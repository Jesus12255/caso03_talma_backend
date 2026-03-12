from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config.config import settings
from core.context.user_context import UserSession, set_user_session
from app.auth.service.token_blocklist_service import TokenBlocklistService
from datetime import datetime, timezone

def debug_log(message: str):
    with open("auth_debug.log", "a") as f:
        timestamp = datetime.now(timezone.utc).isoformat()
        f.write(f"[{timestamp}] [DEP] {message}\n")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    request: Request
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "access":
            debug_log(f"Invalid token type or email missing: email={email}, type={token_type}")
            raise credentials_exception
            
        is_blocked = await TokenBlocklistService.is_blocklisted(jti)
        debug_log(f"Checking JTI {jti}: Blocklisted={is_blocked}")
        if is_blocked:
            debug_log(f"REJECTING REVOKED TOKEN: {jti}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else None
        # Verificar si viene a través de proxy (X-Forwarded-For)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
            
        session = UserSession(
            email=email, 
            username=payload.get("usuario"),
            user_id=payload.get("usuarioId"),
            full_name=payload.get("nombre"),
            role_id=payload.get("rolId"),
            role_code=payload.get("rolCodigo"),
            role_name=payload.get("rol"),
            ip_address=client_ip
        )
        set_user_session(session)
        
        return email
    except JWTError:
        raise credentials_exception

async def verify_websocket_token(token: str) -> dict | None:
    """Verifica un JWT token crudo proveniente de un WebSocket"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        token_type: str = payload.get("type")
        
        if not email or token_type != "access":
            return None
            
        if await TokenBlocklistService.is_blocklisted(jti):
            return None
            
        return {
            "email": email,
            "user_id": payload.get("usuarioId"),
            "role_id": payload.get("rolId"),
            "role_code": payload.get("rolCodigo"),
            "role_name": payload.get("rol")
        }
    except JWTError:
        return None
