
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.auth.schema.user import UserCreate, User
from app.security.domain.Usuario import Usuario

class UserRepository:
    async def get_by_email_or_username(self, db: AsyncSession, identifier: str) -> Optional[User]:
        # Search by correo OR usuario
        result = await db.execute(select(Usuario).where(
            or_(Usuario.correo == identifier, Usuario.usuario == identifier)
        ))
        usuario = result.scalars().first()
        if usuario:
            return User(
                id=str(usuario.usuario_id),
                email=usuario.correo if usuario.correo else "", # Handle missing email if strictly username login? Schema requires email.
                # If email is missing in DB but schema requires it, this might fail validation if passed empty. 
                # Let's assume valid users have emails or relax User schema later if needed.
                full_name=f"{usuario.primer_nombre or ''} {usuario.apellido_paterno or ''} {usuario.apellido_materno or ''}".strip(),
                is_active=True
            )
        return None

    # Helper method to get the raw ORM object (including password hash)
    async def get_user_orm_by_identifier(self, db: AsyncSession, identifier: str) -> Optional[Usuario]:
         result = await db.execute(select(Usuario).where(
            or_(Usuario.correo == identifier, Usuario.usuario == identifier)
        ))
         return result.scalars().first()

    # Keeping original method signature for compatibility if interface requires 'get_by_email'
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await self.get_by_email_or_username(db, email)
        
    async def get_user_orm_by_email(self, db: AsyncSession, email: str) -> Optional[Usuario]:
        return await self.get_user_orm_by_identifier(db, email)

    async def update_password(self, db: AsyncSession, email: str, new_hashed_password: str) -> bool:
        # Update via identifier (handling email input mainly for this flow)
        user_orm = await self.get_user_orm_by_identifier(db, email)
        if user_orm:
            user_orm.password = new_hashed_password
            db.add(user_orm)
            await db.commit()
            await db.refresh(user_orm)
            return True
        return False
