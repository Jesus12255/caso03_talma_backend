from typing import Any
from sqlalchemy import func, select
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from app.core.repository.guia_aerea_filtro_repository import GuiaAereaFiltroRepository
from app.integration.impl.base_repository_impl import BaseRepositoryImpl


class GuiaAereaFiltroRepositoryImpl(BaseRepositoryImpl[GuiaAereaDataGrid], GuiaAereaFiltroRepository):
    def __init__(self, db):
        super().__init__(GuiaAereaDataGrid, db)

    async def find_data_grid(self, filters: list, start: int, limit: int, sort: str = None) -> tuple[Any, int]:
        query = select(GuiaAereaDataGrid)
        if filters:
            for condition in filters:
                query = query.where(condition)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        if sort:
             pass 
        else:
             query = query.order_by(GuiaAereaDataGrid.fecha_consulta.desc())
        query = query.offset(start).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total_count