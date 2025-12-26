
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int | str
    is_active: bool = True

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserForgotPassword(BaseModel):
    email: EmailStr

class UserVerifyCode(BaseModel):
    email: EmailStr
    code: str

class UserResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=8)
