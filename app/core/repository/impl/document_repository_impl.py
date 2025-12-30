from sqlalchemy.ext.asyncio import AsyncSession
from app.core.domain.guia_aerea import  GuiaAerea
from sqlalchemy import select

from app.core.repository.document_repository import DocumentRepository
from app.integration.impl.base_repository_impl import BaseRepositoryImpl



class DocumentRepositoryImpl(BaseRepositoryImpl[GuiaAerea], DocumentRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(GuiaAerea, db)

    async def find_by_numero(self, numero: str, exclude_id: str = None) -> GuiaAerea | None:
        query = select(GuiaAerea).where(GuiaAerea.numero == numero)
        if exclude_id:
             query = query.where(GuiaAerea.guia_aerea_id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_id_with_relations(self, id: str) -> GuiaAerea | None:
        from sqlalchemy.orm import selectinload
        query = select(GuiaAerea).where(GuiaAerea.guia_aerea_id == id).options(
            selectinload(GuiaAerea.confianzas_extraccion)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    