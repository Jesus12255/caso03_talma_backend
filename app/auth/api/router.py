
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from app.auth.schema.user import UserCreate, User, UserLogin, Token
from app.auth.service.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/signup", response_model=User)
async def signup(user: UserCreate):
    return auth_service.signup(user)

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    return auth_service.login(user)

@router.get("/me", response_model=User)
async def get_current_user():
    return User(id=1, email="test@example.com", full_name="Test User", is_active=True)
