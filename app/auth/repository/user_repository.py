
from typing import Dict, Optional
from app.auth.schema.user import UserCreate, User

# In-memory mock database
fake_users_db: Dict[str, dict] = {}

class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        if email in fake_users_db:
             user_dict = fake_users_db[email]
             return User(**user_dict)
        return None

    def create(self, user: UserCreate) -> User:
        user_id = len(fake_users_db) + 1
        user_obj = User(
            id=user_id,
            email=user.email,
            full_name=user.full_name,
            is_active=True
        )
        # Store password plainly for mock (in real app, hash it!)
        fake_users_db[user.email] = user_obj.model_dump()
        fake_users_db[user.email]["hashed_password"] = user.password # Simulated hash
        return user_obj
