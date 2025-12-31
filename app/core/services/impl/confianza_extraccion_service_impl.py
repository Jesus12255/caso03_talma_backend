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
      
        remitente_id = request.intervinientes[0].intervinienteId
        consignatario_id = request.intervinientes[1].intervinienteId
        guia_id = request.guiaAereaId

        confianzas_to_save = []
        for confianza_dto in request.confianzas:
            confianza = Mapper.to_entity(confianza_dto, ConfianzaExtraccion)
            campo = confianza.nombre_campo
            if campo.startswith("remitente."):
                confianza.interviniente_id = remitente_id
            elif campo.startswith("consignatario."):
                confianza.interviniente_id = consignatario_id
            
            confianza.guia_aerea_id = guia_id

            confianza.creado = DateUtil.get_current_local_datetime()
            confianza.creado_por = self.session.full_name
            confianzas_to_save.append(confianza)
        
        if confianzas_to_save:
            await self.confianza_extraccion_repository.save_all(confianzas_to_save)