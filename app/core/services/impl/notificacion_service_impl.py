from core.exceptions import AppBaseException
from uuid import UUID
from app.core.services.notificacion_service import NotificacionService
from utl.date_util import DateUtil
from utl.constantes import Constantes
from config.mapper import Mapper
from core.service.service_base import ServiceBase
from app.core.domain.notificacion import Notificacion
from dto.notificacion import NotificacionRequest
from app.core.repository.notificacion_repository import NotificacionRepository
from core.realtime.publisher import publish_user_notification

class NotificacionServiceImpl(NotificacionService, ServiceBase):

    def __init__(self, notificacion_repository: NotificacionRepository):
        self.notificacion_repository = notificacion_repository
    
    async def save(self, t: NotificacionRequest):
        notificacion = Mapper.to_entity(t, Notificacion)
        notificacion.estado_codigo = Constantes.EstadoNotificacion.PENDIENTE
        notificacion.creado = DateUtil.get_current_local_datetime()
        notificacion.creado_por = Constantes.SYSTEM_USER
        notificacion.habilitado = Constantes.HABILITADO
        await self.notificacion_repository.save(notificacion)
        
        
        await publish_user_notification(
            user_id=str(notificacion.usuario_id),
            type=t.tipoCodigo,
            message=t.mensaje,
            doc_id=str(notificacion.guia_aerea_id) if notificacion.guia_aerea_id else None,
            title=t.titulo,
            severity=t.severidadCodigo,
            is_persistent=True,
            notification_id=str(notificacion.notificacion_id)
        )

    async def get_user_notifications(self, user_id: str):
        entities = await self.notificacion_repository.find_by_user_id(user_id)
        return entities

    async def visto(self, notificacion_id: UUID):
        notificacion = await self.notificacion_repository.get_by_id(notificacion_id)
        if not notificacion:
            raise AppBaseException("Notificacion no encontrada")
        notificacion.estado_codigo = Constantes.EstadoNotificacion.LEIDO
        notificacion.modificado = DateUtil.get_current_local_datetime()
        notificacion.modificado_por = self.session.full_name
        await self.notificacion_repository.save(notificacion)

    async def resolver(self, guia_aerea_id: UUID):
        notificaciones = await self.notificacion_repository.find_by_guia_aerea_id(guia_aerea_id)
        if not notificaciones:
            return
            
        modificado_por = getattr(self.session, 'full_name', None) or 'SYSTEM'
            
        for notificacion in notificaciones:
            notificacion.estado_codigo = Constantes.EstadoNotificacion.RESUELTO
            notificacion.modificado = DateUtil.get_current_local_datetime()
            notificacion.modificado_por = modificado_por
            notificacion.habilitado = Constantes.INHABILITADO
            
            await self.notificacion_repository.save(notificacion)
            
            try:
                await publish_user_notification(
                    user_id=str(notificacion.usuario_id),
                    type=Constantes.EstadoNotificacion.RESUELTO,
                    is_persistent=False,
                    notification_id=str(notificacion.notificacion_id)
                )
            except Exception as e:
                print(f"Error publishing resolution event: {e}")


        
    async def get(self, notificacion_id: UUID) -> Notificacion:
        notificacion = await self.notificacion_repository.get_by_id(notificacion_id)
        if not notificacion:
            raise AppBaseException("Notificacion no encontrada")
        return notificacion