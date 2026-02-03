from app.core.facade.notificacion_facade import NotificacionFacade
from app.core.services.notificacion_service import NotificacionService
from uuid import UUID
from core.facade.facade_base import FacadeBase
from dto.universal_dto import BaseOperacionResponse
class NotificacionFacadeImpl(NotificacionFacade, FacadeBase):

    def init(self, notificacion_service: NotificacionService):
        self.notificacion_service = notificacion_service

    async def visto(self, notificacion_id: UUID):
        await self.notificacion_service.visto(notificacion_id)
        return BaseOperacionResponse(codigo=200, mensaje="Notificacion vista exitosamente")
        
