from uuid import UUID
from utl.constantes import Constantes
from app.core.domain.notificacion import Notificacion
from app.core.repository.notificacion_repository import NotificacionRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text

class NotificacionRepositoryImpl(NotificacionRepository):
    
    
    def __init__(self, db: AsyncSession):
        super().__init__(Notificacion, db)

    async def find_by_user_id(self, user_id: str):
        query = select(Notificacion).where(
            Notificacion.usuario_id == user_id,
            Notificacion.estado_codigo != Constantes.EstadoNotificacion.RESUELTO,
            Notificacion.estado_codigo != Constantes.EstadoNotificacion.ARCHIVADO
        ).order_by(desc(Notificacion.creado))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_by_guia_aerea_id(self, guia_aerea_id: UUID) -> Notificacion:
        query = select(Notificacion).where(
            Notificacion.guia_aerea_id == guia_aerea_id,
            Notificacion.estado_codigo == Constantes.EstadoNotificacion.PENDIENTE,
            Notificacion.habilitado == Constantes.HABILITADO
        ).order_by(desc(Notificacion.creado))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_high_risk_alerts(self, min_score: int = 40) -> list[Notificacion]:
        # Query JSONB metadata field for 'score_riesgo'
        query = select(Notificacion).where(
            Notificacion.tipo_codigo == "IRREGULARIDAD",
            text(f"CAST(metadata->>'score_riesgo' AS INTEGER) >= {min_score}")
        ).order_by(desc(Notificacion.creado))
        
        result = await self.db.execute(query)
        return result.scalars().all()