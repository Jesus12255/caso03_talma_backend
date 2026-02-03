from uuid import UUID
from utl.constantes import Constantes
from app.core.domain.notificacion import Notificacion
from app.core.repository.notificacion_repository import NotificacionRepository
from sqlalchemy.ext.asyncio import AsyncSession

class NotificacionRepositoryImpl(NotificacionRepository):
    
    
    def __init__(self, db: AsyncSession):
        super().__init__(Notificacion, db)

    async def find_by_user_id(self, user_id: str):
        from sqlalchemy import select, desc
        query = select(Notificacion).where(
            Notificacion.usuario_id == user_id,
            Notificacion.estado_codigo != Constantes.EstadoNotificacion.RESUELTO,
            Notificacion.estado_codigo != Constantes.EstadoNotificacion.ARCHIVADO
        ).order_by(desc(Notificacion.creado))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_by_guia_aerea_id(self, guia_aerea_id: UUID) -> Notificacion:
        from sqlalchemy import select, desc
        query = select(Notificacion).where(
            Notificacion.guia_aerea_id == guia_aerea_id,
            Notificacion.estado_codigo == Constantes.EstadoNotificacion.PENDIENTE,
            Notificacion.tipo_codigo == Constantes.TipoNotificacion.OBSERVACION,
            Notificacion.habilitado == Constantes.HABILITADO
        ).order_by(desc(Notificacion.creado))
        result = await self.db.execute(query)
        return result.scalars().all()





        