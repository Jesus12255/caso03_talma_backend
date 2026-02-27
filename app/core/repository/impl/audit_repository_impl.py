from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.domain.audit import Audit
from app.core.repository.audit_repository import AuditRepository


class AuditRepositoryImpl(AuditRepository):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Audit, db)
    
    async def find_by_entidad(
        self,
        entidad_tipo: str,
        entidad_id: str,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        usuario_id: Optional[str] = None,
        accion_tipo: Optional[str] = None,
        limit: int =100,
        offset: int = 0
    ) -> List[Audit]:
        filters = [
            Audit.entidad_tipo_codigo == entidad_tipo,
            Audit.entidad_id == UUID(entidad_id)
        ]
        
        if fecha_desde:
            filters.append(Audit.fecha_hora>= fecha_desde)
        
        if fecha_hasta:
            filters.append(Audit.fecha_hora <= fecha_hasta)
        
        if usuario_id:
            filters.append(Audit.usuario_id == UUID(usuario_id))
        
        if accion_tipo:
            filters.append(Audit.accion_tipo_codigo == accion_tipo)
        
        query = (
            select(Audit)
            .where(and_(*filters))
            .order_by(desc(Audit.fecha_hora))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
