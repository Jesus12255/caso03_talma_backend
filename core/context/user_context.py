from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserSession:
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[str] = None
    role_code: Optional[str] = None
    role_name: Optional[str] = None
    ip_address: Optional[str] = None



_user_session_ctx_var: ContextVar[Optional[UserSession]] = ContextVar("user_session", default=None)

def get_user_session() -> Optional[UserSession]:
    return _user_session_ctx_var.get()

def set_user_session(session: UserSession):
    _user_session_ctx_var.set(session)
