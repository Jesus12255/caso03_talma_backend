from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config.config import settings
from core.context.user_context import UserSession, set_user_session

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
        
        if email is None:
            raise credentials_exception
        
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
