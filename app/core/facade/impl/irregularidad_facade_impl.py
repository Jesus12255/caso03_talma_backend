from utl.constantes import Catalogo
from app.configuration.facade.comun_facade import ComunFacade
from dto.perfil_riesgo_dtos import PerfilRiesgoComboResponse
from config.mapper import Mapper
from dto.perfil_riesgo_dtos import PerfilRiesgoDataGridResponse, PerfilRiesgoResponse, PerfilRiesgoDispersionResponse
from dto.collection_response import CollectionResponse
from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest
from app.core.services.perfil_riesgo_service import PerfilRiesgoService
from dto.universal_dto import BaseOperacionResponse
from uuid import UUID
from app.core.services.IrregularidadService import IrregularidadService
from app.core.facade.irregularidad_facade import IrregularidadFacade
from core.facade.facade_base import FacadeBase

class IrregularidadFacadeImpl(IrregularidadFacade, FacadeBase):

    def __init__(self, irregularidad_service: IrregularidadService, perfil_riesgo_service: PerfilRiesgoService, comun_facade: ComunFacade):
        self.irregularidad_service = irregularidad_service
        self.perfil_riesgo_service = perfil_riesgo_service
        self.comun_facade = comun_facade

    async def validarExcepcion(self, notificacion_id: UUID) -> BaseOperacionResponse:
        await self.irregularidad_service.validarExcepcion(notificacion_id)
        return BaseOperacionResponse(codigo="200", mensaje="Excepción validada correctamente.")

    async def findPerfiles(self, request: PerfilRiesgoFiltroRequest) -> CollectionResponse[PerfilRiesgoDataGridResponse]:
        data, total_count = await self.perfil_riesgo_service.find(request)
        elements = [Mapper.to_dto(x, PerfilRiesgoDataGridResponse) for x in data]
        return CollectionResponse[PerfilRiesgoDataGridResponse](
            elements=elements,
            totalCount=total_count,
            start=request.start,
            limit=request.limit
        )

    async def initFindPerfiles(self) -> PerfilRiesgoComboResponse:
        return PerfilRiesgoComboResponse(
            tipoInterviniente = await self.comun_facade.load_by_referencia_nombre(Catalogo.TIPO_INTERVINIENTE)
        )

    async def getPerfilById(self, id: str) -> PerfilRiesgoResponse:
        domain_obj = await self.perfil_riesgo_service.getPerfilById(id)
        return Mapper.to_dto(domain_obj, PerfilRiesgoResponse)

    async def getPerfilDispersion(self, id: str) -> PerfilRiesgoDispersionResponse:
        data = await self.perfil_riesgo_service.get_dispersion(id)
        return Mapper.to_dto(data, PerfilRiesgoDispersionResponse)
