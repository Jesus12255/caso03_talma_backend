from app.core.domain.confianza_extraccion import ConfianzaExtraccion
from app.core.repository.confianza_extraccion_repository import ConfianzaExtraccionRepository
from app.core.services.confianza_extraccion_service import ConfianzaExtraccionService
from config.mapper import Mapper
from core.service.service_base import ServiceBase
from dto.guia_aerea_dtos import GuiaAereaRequest
from utl.date_util import DateUtil


class ConfianzaExtraccionServiceImpl(ConfianzaExtraccionService, ServiceBase):

    def __init__(self, confianza_extraccion_repository: ConfianzaExtraccionRepository):
        self.confianza_extraccion_repository = confianza_extraccion_repository

    async def save(self, request: GuiaAereaRequest):
        for confianza_dto in request.confianzas:
            confianza = Mapper.to_entity(confianza_dto, ConfianzaExtraccion)
            if confianza.guia_aerea_id :
                confianza.guia_aerea_id = request.guiaAereaId
            
            confianza.creado = DateUtil.get_current_local_datetime()
            confianza.creado_por = self.session.full_name
            await self.confianza_extraccion_repository.save(confianza)