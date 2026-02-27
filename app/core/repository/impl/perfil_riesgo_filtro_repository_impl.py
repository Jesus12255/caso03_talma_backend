from app.core.repository.perfil_riesgo_filtro_repository import PerfilRiesgoFiltroRepository
from app.core.domain.perfil_riesgo_data_grid import PerfilRiesgoDataGrid
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from typing import Any
from sqlalchemy import func, select

class PerfilRiesgoFiltroRepositoryImpl(BaseRepositoryImpl[PerfilRiesgoDataGrid], PerfilRiesgoFiltroRepository):
    
    def __init__(self, db):
        super().__init__(PerfilRiesgoDataGrid, db)


    async def find_data_grid(self, filters: list, start: int, limit: int, sort: str = None) -> tuple[Any, int]:
        query = select(PerfilRiesgoDataGrid)
        if filters:
            for condition in filters:
                query = query.where(condition)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        if sort:
             pass 
        else:
             query = query.order_by(PerfilRiesgoDataGrid.creado.desc())
        query = query.offset(start).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total_count