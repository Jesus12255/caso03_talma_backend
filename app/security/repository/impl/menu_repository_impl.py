from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.security.repository.menu_repository import MenuRepository
from app.security.domain.menu_maestro import MenuMaestro
from app.security.domain.menu_rol import MenuRol

class MenuRepositoryImpl(MenuRepository):
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_enabled(self) -> List[MenuMaestro]:
        query = select(MenuMaestro).where(MenuMaestro.habilitado == True).order_by(MenuMaestro.orden)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_by_rol_id(self, rol_id: str) -> List[MenuMaestro]:
        query = (
            select(MenuMaestro)
            .join(MenuRol, MenuMaestro.menu_maestro_id == MenuRol.menu_maestro_id)
            .where(MenuRol.rol_id == rol_id, MenuRol.habilitado == True, MenuMaestro.habilitado == True)
            .order_by(MenuMaestro.orden)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
