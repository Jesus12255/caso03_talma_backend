
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.auth.schema.user import User, UserLogin, Token, UserForgotPassword, UserVerifyCode, UserResetPassword, TokenRefresh, LogoutRequest
from app.auth.service.impl.auth_service_impl import AuthServiceImpl
from app.core.services.impl.email_service_impl import EmailServiceImpl
from config.database_config import get_db
from config.config import settings

router = APIRouter()
email_service = EmailServiceImpl()
auth_service = AuthServiceImpl(email_service=email_service)

from app.auth.dependencies.dependencies_auth import get_current_user as auth_dep, oauth2_scheme
from core.context.user_context import get_user_session

# --- Configuración de cookie ---
_COOKIE_NAME = "refresh_token"
_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 días en segundos
_IS_PRODUCTION = settings.ENVIRONMENT == "production"


@router.post("/login", response_model=Token)
async def login(user: UserLogin, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    token_data = await auth_service.login(db, user, ip=client_ip)

    # Mover el refresh_token a una cookie HttpOnly: inaccesible para scripts JS
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token_data.refresh_token,
        httponly=True,
        secure=_IS_PRODUCTION,   # Solo HTTPS en producción
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/v1/auth/refresh",  # Limitar scope de la cookie al endpoint de refresh
    )

    # Devolver solo el access_token en el body; el refresh ya va en la cookie
    return Token(
        access_token=token_data.access_token,
        refresh_token="",  # Omitido intencionalmente — viaja en cookie HttpOnly
        token_type=token_data.token_type,
        expires_in=token_data.expires_in,
        require_password_change=token_data.require_password_change,
    )


@router.post("/forgot-password")
async def forgot_password(user: UserForgotPassword, db: AsyncSession = Depends(get_db)):
    """
    Initiates the password recovery process.
    """
    message = await auth_service.forgot_password(db, user.email)
    return {"message": message}


@router.post("/verify-code")
async def verify_code(user: UserVerifyCode, db: AsyncSession = Depends(get_db)):
    """
    Verifies the code sent to the email.
    """
    is_valid = await auth_service.verify_code(db, user.email, user.code)
    if is_valid:
        return {"message": "Code verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid code")


@router.post("/reset-password")
async def reset_password(user: UserResetPassword, db: AsyncSession = Depends(get_db)):
    """
    Resets the password using the code and new password.
    """
    success = await auth_service.reset_password(db, user.email, user.code, user.new_password)
    if success:
         return {"message": "Password reset successfully"}
    raise HTTPException(status_code=400, detail="Failed to reset password")


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    body: TokenRefresh | None = None,
):
    """
    Refreshes the access token.
    Priority: cookie HttpOnly > body (retrocompatibilidad).
    """
    # 1. Leer desde cookie HttpOnly (método seguro)
    token = request.cookies.get(_COOKIE_NAME)

    # 2. Fallback: body JSON (para clientes que aún no envían cookie)
    if not token and body:
        token = body.refresh_token

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    token_data = await auth_service.refresh_token(db, token)

    # Rotar la cookie con el nuevo refresh_token
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token_data.refresh_token,
        httponly=True,
        secure=_IS_PRODUCTION,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/v1/auth/refresh",
    )

    return Token(
        access_token=token_data.access_token,
        refresh_token="",  # Omitido intencionalmente
        token_type=token_data.token_type,
        expires_in=token_data.expires_in,
        require_password_change=token_data.require_password_change,
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    body: LogoutRequest | None = None,
):
    """
    Logs out the user by revoking the access token and clearing the refresh cookie.
    """
    # Obtener refresh_token desde la cookie (preferido) o del body (retrocompat)
    refresh = request.cookies.get(_COOKIE_NAME)
    if not refresh and body:
        refresh = body.refresh_token

    await auth_service.logout(access_token=token, refresh_token=refresh)

    # Eliminar la cookie del navegador del cliente
    response.delete_cookie(key=_COOKIE_NAME, path="/api/v1/auth/refresh")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_me(email: str = Depends(auth_dep)):
    session = get_user_session()
    return User(
        id=session.user_id,
        email=session.email,
        full_name=session.full_name,
        role=session.role_code,
        is_active=True
    )
