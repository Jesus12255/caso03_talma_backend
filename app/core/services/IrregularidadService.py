from uuid import UUID
from app.core.domain.guia_aerea import GuiaAerea
from abc import ABC, abstractmethod


from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest, RedVinculosResponse

class IrregularidadService(ABC):

    @abstractmethod
    async def detectar_irregularidades(self, guia: GuiaAerea) -> dict:
        pass

    @abstractmethod
    async def validarExcepcion(self, notificacion_id: UUID):
        pass

    @abstractmethod
    async def validar(self, guia: GuiaAerea ):
        pass

    @abstractmethod
    async def getRedVinculos(self, request: PerfilRiesgoFiltroRequest) -> RedVinculosResponse:
        pass