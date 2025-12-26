
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.schema.user import UserLogin, Token

class AuthService(ABC):
    @abstractmethod
    async def login(self, db: AsyncSession, user_in: UserLogin) -> Token:
        pass

    @abstractmethod
    async def forgot_password(self, db: AsyncSession, email: str) -> str:
        pass

    @abstractmethod
    async def verify_code(self, db: AsyncSession, email: str, code: str) -> bool:
        pass

    @abstractmethod
    async def reset_password(self, db: AsyncSession, email: str, code: str, new_password: str) -> bool:
        pass
