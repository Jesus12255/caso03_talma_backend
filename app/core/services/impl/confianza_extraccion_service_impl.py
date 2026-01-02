from typing import Any
from app.core.domain.confianza_extraccion import ConfianzaExtraccion
from app.core.repository.confianza_extraccion_repository import ConfianzaExtraccionRepository
from app.core.services.confianza_extraccion_service import ConfianzaExtraccionService
from config.mapper import Mapper
from core.service.service_base import ServiceBase
from dto.guia_aerea_dtos import GuiaAereaRequest
from utl.date_util import DateUtil
from utl.constantes import Constantes

class ConfianzaExtraccionServiceImpl(ConfianzaExtraccionService, ServiceBase):

    def __init__(self, confianza_extraccion_repository: ConfianzaExtraccionRepository):
        self.confianza_extraccion_repository = confianza_extraccion_repository


    