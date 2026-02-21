from sqlalchemy.ext.asyncio import AsyncSession
from app.core.domain.guia_aerea import  GuiaAerea
from sqlalchemy import select, func, distinct
import uuid
from sqlalchemy.orm import selectinload

from app.core.repository.document_repository import DocumentRepository
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from utl.constantes import Constantes
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from datetime import datetime, timedelta
from typing import List



class DocumentRepositoryImpl(BaseRepositoryImpl[GuiaAerea], DocumentRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(GuiaAerea, db)

    async def find_by_numero(self, numero: str, exclude_id: str = None) -> GuiaAerea | None:
        query = select(GuiaAerea).where(GuiaAerea.numero == numero, GuiaAerea.habilitado.is_(Constantes.HABILITADO))
        if exclude_id:
             try:
                 uuid_obj = uuid.UUID(exclude_id)
                 query = query.where(GuiaAerea.guia_aerea_id != uuid_obj)
             except ValueError:
                 # If ID is invalid, safely ignore exclusion
                 pass
        
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_id_with_relations(self, id: str) -> GuiaAerea | None:
        query = select(GuiaAerea).where(GuiaAerea.guia_aerea_id == id).options(
            selectinload(GuiaAerea.intervinientes)
        )
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def find_recent_by_consignee_names(self, nombres: List[str], hours: int = 24) -> List[GuiaAerea]:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        query = select(GuiaAerea).join(GuiaAerea.intervinientes).where(
            GuiaAereaInterviniente.nombre.in_(nombres),
            GuiaAereaInterviniente.rol_codigo == Constantes.TipoInterviniente.CONSIGNATARIO,
            GuiaAerea.creado >= cutoff_time
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_unique_consignees_for_sender(self, sender_names: List[str]) -> int:
        # Subquery to find GuiaAerea IDs where the sender is present (using any variation)
        sender_subquery = (
            select(GuiaAereaInterviniente.guia_aerea_id)
            .where(
                GuiaAereaInterviniente.nombre.in_(sender_names),
                GuiaAereaInterviniente.rol_codigo == Constantes.TipoInterviniente.REMITENTE
            )
        )

        query = select(func.count(distinct(GuiaAereaInterviniente.nombre))).where(
            GuiaAereaInterviniente.guia_aerea_id.in_(sender_subquery),
            GuiaAereaInterviniente.rol_codigo == Constantes.TipoInterviniente.CONSIGNATARIO
        )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    
