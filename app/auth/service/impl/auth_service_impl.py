
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from jose import jwt, JWTError
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
import random
import uuid
import httpx

from app.auth.service.token_blocklist_service import TokenBlocklistService

from app.auth.service.auth_service import AuthService
from app.auth.repository.user_repository import UserRepository
from app.auth.schema.user import UserLogin, Token
from app.auth.service.login_protection_service import LoginProtectionService
from app.core.services.email_service import EmailService
from app.core.services.impl.email_service_impl import EmailServiceImpl
from core.exceptions import AppBaseException
from config.config import settings
from utl.security_util import SecurityUtil

def debug_log(message: str):
    with open("auth_debug.log", "a") as f:
        timestamp = datetime.utcnow().isoformat()
        f.write(f"[{timestamp}] {message}\n")

# Keep in-memory for codes for now as discussed
# Structure: {email: {"code": str, "expiry": datetime}}
fake_verification_codes: Dict[str, Dict] = {}

class AuthServiceImpl(AuthService):
    def __init__(self, email_service: EmailService = None):
        self.user_repository = UserRepository()
        self.email_service = email_service or EmailServiceImpl()

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=15)
        to_encode.update({
            "exp": expire,
            "jti": str(uuid.uuid4()),
            "type": "access"
        })
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "jti": str(uuid.uuid4()),
            "type": "refresh"
        })
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def login(self, db: AsyncSession, user_in: UserLogin, ip: str = "unknown") -> Token:
        # 1. Check for lockout
        await LoginProtectionService.check_lockout(user_in.email, ip)

        # 2. Verify reCAPTCHA
        if settings.RECAPTCHA_SECRET_KEY:
            if not user_in.recaptcha_token:
                raise AppBaseException("reCAPTCHA validation failed", status_code=status.HTTP_400_BAD_REQUEST)
            
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": settings.RECAPTCHA_SECRET_KEY,
                        "response": user_in.recaptcha_token,
                        "remoteip": ip
                    }
                )
                result = res.json()
                
                # Check for success and minimum score for v3 (e.g., 0.5)
                # It's standard practice to accept 0.5 as "likely human"
                is_success = result.get("success", False)
                score = result.get("score", 0.0)
                action = result.get("action", "")

                if not is_success or score < 0.5 or action != "login":
                    logger_msg = f"Failed reCAPTCHA v3 for {user_in.email} from {ip}: {result}"
                    debug_log(logger_msg)
                    raise AppBaseException("reCAPTCHA validation failed or score too low", status_code=status.HTTP_400_BAD_REQUEST)

        # Get ORM user to check password hash
        user_orm = await self.user_repository.get_user_orm_by_email(db, user_in.email)
        
        # Consistent generic error message for security
        generic_error = "Incorrect email or password"

        if not user_orm:
            await LoginProtectionService.register_failure(user_in.email, ip)
            raise AppBaseException(generic_error, status_code=status.HTTP_400_BAD_REQUEST)
        
        if not user_orm.habilitado:
            # We don't necessarily register failure for disabled users (they aren't guessing), 
            # but we show a specific message as it's an administrative state.
            raise AppBaseException("El usuario se encuentra inhabilitado. Por favor, contacte al administrador.", status_code=status.HTTP_403_FORBIDDEN)
        
        stored_hash = user_orm.password

        # Security check
        if not stored_hash or not SecurityUtil.verify_password(user_in.password, stored_hash):
            await LoginProtectionService.register_failure(user_in.email, ip)
            raise AppBaseException(generic_error, status_code=status.HTTP_400_BAD_REQUEST)

        # 2. Reset attempts on success
        await LoginProtectionService.reset_attempts(user_in.email, ip)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": user_orm.correo,
            "usuarioId": str(user_orm.usuario_id), 
            "usuario": user_orm.usuario, 
            "nombre":  f"{user_orm.primer_nombre or ''} {user_orm.segundo_nombre or ''} {user_orm.apellido_paterno or ''} {user_orm.apellido_materno or ''}".replace("  ", " ").strip(),
            "rolId": str(user_orm.rol.rol_id) if user_orm.rol else None, 
            "rolCodigo": user_orm.rol.codigo if user_orm.rol else None,
            "rol": user_orm.rol.nombre if user_orm.rol else None
        }
        access_token = self.create_access_token(data=token_data, expires_delta=access_token_expires)
        
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = self.create_refresh_token(data={"sub": user_orm.correo}, expires_delta=refresh_token_expires)
        
        # Check if using default password
        require_change = False
        if user_in.password == settings.PASWORD_INICIAL:
            require_change = True
            
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            require_password_change=require_change
        )

    async def forgot_password(self, db: AsyncSession, email: str) -> str:
        # Check if user exists in DB
        user = await self.user_repository.get_by_email(db, email)
        
        # Standardized generic response
        success_msg = f"Si el correo está registrado, recibirás un mensaje con las instrucciones para restablecer tu contraseña."

        if not user:
            # We don't do anything, but we return the same message as if we did
            return success_msg

        code = str(random.randint(100000, 999999))
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(minutes=5)
        fake_verification_codes[email] = {"code": code, "expiry": expiry}
        
        print(f"DEBUG: Verification code for {email} is {code} (expires at {expiry} UTC)") 

        # Send email
        nombre_completo = user.full_name or "Usuario"
        email_sent = self.email_service.send_verification_code(email, code, nombre_completo)
        
        if not email_sent:
            print(f"ERROR: Failed to send verification email to {email}")

        return success_msg

    async def verify_code(self, db: AsyncSession, email: str, code: str) -> bool:
        data = fake_verification_codes.get(email)
        
        if not data:
            raise AppBaseException("Invalid verification code", status_code=status.HTTP_400_BAD_REQUEST)

        stored_code = data.get("code")
        expiry = data.get("expiry")

        if stored_code != code:
            raise AppBaseException("Invalid verification code", status_code=status.HTTP_400_BAD_REQUEST)

        if datetime.utcnow() > expiry:
            del fake_verification_codes[email]
            raise AppBaseException("Verification code has expired", status_code=status.HTTP_400_BAD_REQUEST)

        return True

    async def reset_password(self, db: AsyncSession, email: str, code: str, new_password: str) -> bool:
        if not await self.verify_code(db, email, code):
             return False
        
        hashed_pwd = SecurityUtil.get_password_hash(new_password)
        success = await self.user_repository.update_password(db, email, hashed_pwd)
        
        if not success:
             raise AppBaseException("User not found", status_code=status.HTTP_404_NOT_FOUND)
             
        if email in fake_verification_codes:
            del fake_verification_codes[email]
            
        return True

    async def logout(self, access_token: str, refresh_token: str | None = None) -> bool:
        """Revokes both access token and refresh token by adding their JTIs to the blocklist."""
        debug_log(f"LOGOUT CALLED. Access token present: {bool(access_token)}")
        try:
            now_ts = datetime.now(timezone.utc).timestamp()
            
            # Revoke access token
            if access_token:
                payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
                jti = payload.get("jti")
                exp = payload.get("exp")
                debug_log(f"Access Token JTI: {jti}, EXP: {exp}, NOW_TS: {now_ts}")
                if jti and exp:
                    expire_seconds = max(1, int(exp - now_ts)) # Force at least 1s if somehow negative but close
                    debug_log(f"Expiring Access JTI in {expire_seconds} seconds")
                    await TokenBlocklistService.add_to_blocklist(jti, expire_seconds)
            
            # Revoke refresh token
            if refresh_token:
                payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
                jti = payload.get("jti")
                exp = payload.get("exp")
                debug_log(f"Refresh Token JTI: {jti}, EXP: {exp}, NOW_TS: {now_ts}")
                if jti and exp:
                    expire_seconds = max(1, int(exp - now_ts))
                    debug_log(f"Expiring Refresh JTI in {expire_seconds} seconds")
                    await TokenBlocklistService.add_to_blocklist(jti, expire_seconds)
            
            return True
        except Exception as e:
            debug_log(f"LOGOUT FAILED: {str(e)}")
            return True

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> Token:
        """Validates refresh token, blocklists the old one, and generates new token pair."""
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            jti = payload.get("jti")
            email = payload.get("sub")
            token_type = payload.get("type")
            exp = payload.get("exp")
            
            if token_type != "refresh":
                raise AppBaseException("Invalid token type", status_code=status.HTTP_401_UNAUTHORIZED)
                
            if not email or not jti:
                raise AppBaseException("Invalid token payload", status_code=status.HTTP_401_UNAUTHORIZED)

            if await TokenBlocklistService.is_blocklisted(jti):
                raise AppBaseException("Token revoked", status_code=status.HTTP_401_UNAUTHORIZED)
                
            # Blocklist the old refresh token (rotate)
            now_ts = datetime.now(timezone.utc).timestamp()
            expire_seconds = max(1, int(exp - now_ts))
            await TokenBlocklistService.add_to_blocklist(jti, expire_seconds)
                
            # Fetch user to generate new access token
            user_orm = await self.user_repository.get_user_orm_by_email(db, email)
            if not user_orm or not user_orm.habilitado:
                raise AppBaseException("User not found or disabled", status_code=status.HTTP_401_UNAUTHORIZED)

            # Generate new tokens
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {
                "sub": user_orm.correo,
                "usuarioId": str(user_orm.usuario_id), 
                "usuario": user_orm.usuario, 
                "nombre":  f"{user_orm.primer_nombre or ''} {user_orm.segundo_nombre or ''} {user_orm.apellido_paterno or ''} {user_orm.apellido_materno or ''}".replace("  ", " ").strip(),
                "rolId": str(user_orm.rol.rol_id) if user_orm.rol else None, 
                "rolCodigo": user_orm.rol.codigo if user_orm.rol else None,
                "rol": user_orm.rol.nombre if user_orm.rol else None
            }
            new_access_token = self.create_access_token(data=token_data, expires_delta=access_token_expires)
            
            refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            new_refresh_token = self.create_refresh_token(data={"sub": user_orm.correo}, expires_delta=refresh_token_expires)
            
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                require_password_change=False
            )
            
        except jwt.ExpiredSignatureError:
            raise AppBaseException("Refresh token expired", status_code=status.HTTP_401_UNAUTHORIZED)
        except jwt.JWTError:
            raise AppBaseException("Could not validate credentials", status_code=status.HTTP_401_UNAUTHORIZED)
