from config.mapper import Mapper
from dto.notificacion import NotificacionResponse
from app.core.facade.notificacion_facade import NotificacionFacade
from app.core.services.notificacion_service import NotificacionService
from uuid import UUID
from core.facade.facade_base import FacadeBase
from dto.universal_dto import BaseOperacionResponse
class NotificacionFacadeImpl(NotificacionFacade, FacadeBase):

    def __init__(self, notificacion_service: NotificacionService):
        self.notificacion_service = notificacion_service

    async def visto(self, notificacion_id: UUID):
        await self.notificacion_service.visto(notificacion_id)
        return BaseOperacionResponse(codigo=200, mensaje="Notificacion vista exitosamente")
        
    async def load(self) -> list[NotificacionResponse]:
        notificaciones = await self.notificacion_service.get_user_notifications(str(self.session.user_id))
        responses = []
        for tt in notificaciones:
            response = Mapper.to_dto(tt, NotificacionResponse)
            responses.append(response)
        return responses 