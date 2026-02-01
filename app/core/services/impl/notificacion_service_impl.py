from app.core.services.notificacion_service import NotificacionService
from utl.date_util import DateUtil
from utl.constantes import Constantes
from config.mapper import Mapper
from core.service.service_base import ServiceBase
from app.core.domain.notificacion import Notificacion
from dto.notificacion import NotificacionRequest
from app.core.repository.notificacion_repository import NotificacionRepository

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



        
        