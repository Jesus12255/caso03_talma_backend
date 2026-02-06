from utl.constantes import Constantes
from typing import Optional
from app.core.domain.manifiesto import Manifiesto
from app.core.repository.manifiesto_repository import ManifiestoRepository
from app.core.domain.interviniente import Interviniente
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

class ManifiestoRepositoryImpl(ManifiestoRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(Manifiesto, db)

    async def find_by_vuelo_fecha(self, numero_vuelo: str, fecha_vuelo: str) -> Optional[Manifiesto]:
        query = select(Manifiesto).where(
            Manifiesto.numero_vuelo == numero_vuelo,
            Manifiesto.fecha_vuelo == fecha_vuelo, 
            Manifiesto.habilitado == Constantes.HABILITADO
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def find(self, filters: list, start: int, limit: int, sort: Optional[str] = None) -> tuple[list[Manifiesto], int]:
        query = select(Manifiesto)
        
        if filters:
            query = query.where(*filters)
            
        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.scalar(count_query)

        # Sorting
        if sort:
            # Basic sort implementation - extend as needed
            if sort.startswith("-"):
                 field_name = sort[1:]
                 if hasattr(Manifiesto, field_name):
                     query = query.order_by(getattr(Manifiesto, field_name).desc())
            else:
                 field_name = sort
                 if hasattr(Manifiesto, field_name):
                     query = query.order_by(getattr(Manifiesto, field_name).asc())
        else:
             query = query.order_by(Manifiesto.creado.desc())

        # Pagination
        query = query.offset(start).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all(), total_count

    async def get_with_guias(self, manifiesto_id) -> Optional[Manifiesto]:
        from sqlalchemy.orm import selectinload
        from app.core.domain.guia_aerea import GuiaAerea
        query = select(Manifiesto).options(
            selectinload(Manifiesto.guias).selectinload(GuiaAerea.intervinientes)
        ).where(
            Manifiesto.manifiesto_id == manifiesto_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()