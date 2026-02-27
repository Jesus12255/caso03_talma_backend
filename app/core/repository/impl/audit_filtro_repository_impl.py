from app.core.repository.audit_filtro_repository import AuditFiltroRepository
from app.core.domain.auditoria_data_grid import AuditoriaDataGrid
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

class AuditFiltroRepositoryImpl(BaseRepositoryImpl[AuditoriaDataGrid], AuditFiltroRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(AuditoriaDataGrid, db)

    async def find_data_grid(self, filters: list, start: int, limit: int, sort: str = None) -> tuple[Any, int]:
        query = select(AuditoriaDataGrid)
        if filters:
            for condition in filters:
                query = query.where(condition)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        if sort:
             pass 
        else:
             query = query.order_by(AuditoriaDataGrid.creado.desc())
        query = query.offset(start).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total_count