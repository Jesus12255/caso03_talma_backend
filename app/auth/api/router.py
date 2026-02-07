
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.auth.schema.user import User, UserLogin, Token, UserForgotPassword, UserVerifyCode, UserResetPassword
from app.auth.service.impl.auth_service_impl import AuthServiceImpl
from app.core.services.impl.email_service_impl import EmailServiceImpl
from config.database_config import get_db

router = APIRouter()
email_service = EmailServiceImpl()
auth_service = AuthServiceImpl(email_service=email_service)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, user)

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

from app.auth.dependencies.dependencies_auth import get_current_user as auth_dep
from core.context.user_context import get_user_session

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
