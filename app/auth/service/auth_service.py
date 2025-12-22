
from typing import Optional
from app.auth.repository.user_repository import UserRepository
from app.auth.schema.user import UserCreate, User, UserLogin, Token
from core.exceptions import AppBaseException
from fastapi import status

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def signup(self, user_in: UserCreate) -> User:
        if self.user_repository.get_by_email(user_in.email):
             raise AppBaseException("Email already registered", status_code=400)
        return self.user_repository.create(user_in)

    def login(self, user_in: UserLogin) -> Token:
        user = self.user_repository.get_by_email(user_in.email)
        # Mock password verification
        # In real app: verify_password(user_in.password, user.hashed_password)
        if not user:
            raise AppBaseException("Incorrect email or password", status_code=400)
        
        # In real app: check password hash
        
        return Token(access_token=f"fake-token-{user.email}", token_type="bearer")

    def get_current_user_by_token(self, token: str) -> Optional[User]:
        # Mock token decoding
        # if token starts with fake-token-
        if token.startswith("fake-token-"):
            email = token.replace("fake-token-", "")
            return self.user_repository.get_by_email(email)
        raise AppBaseException("Invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED)
