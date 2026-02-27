from dto.perfil_riesgo_dtos import CambiarListaRequest
from dto.perfil_riesgo_dtos import PerfilRiesgoComboResponse
from dto.perfil_riesgo_dtos import PerfilRiesgoDataGridResponse
from dto.collection_response import CollectionResponse
from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest, PerfilRiesgoResponse, PerfilRiesgoDispersionResponse, RedVinculosResponse
from dto.universal_dto import BaseOperacionResponse
from uuid import UUID
from abc import abstractmethod, ABC

class IrregularidadFacade(ABC):
   
    @abstractmethod
    async def validarExcepcion(self, notificacion_id: UUID) -> BaseOperacionResponse:
        pass

    @abstractmethod
    async def findPerfiles(self, request: PerfilRiesgoFiltroRequest) -> CollectionResponse[PerfilRiesgoDataGridResponse]:
        pass

    @abstractmethod
    async def initFindPerfiles(self) -> PerfilRiesgoComboResponse:
        pass

    @abstractmethod
    async def getPerfilById(self, id: str) -> PerfilRiesgoResponse:
        pass

    @abstractmethod
    async def getPerfilDispersion(self, id: str) -> PerfilRiesgoDispersionResponse:
        pass

    @abstractmethod
    async def getRedVinculos(self, request: PerfilRiesgoFiltroRequest) -> RedVinculosResponse:
        pass

    @abstractmethod
    async def cambiarListaPerfil(self, request: CambiarListaRequest) -> BaseOperacionResponse:
        pass
