
from dto.perfil_riesgo_dtos import CambiarListaRequest
from app.core.domain.perfil_riesgo_data_grid import PerfilRiesgoDataGrid
from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest
from abc import ABC, abstractmethod

from app.core.domain.perfil_riesgo import PerfilRiesgo

class PerfilRiesgoService(ABC):

    @abstractmethod
    async def find(self, request: PerfilRiesgoFiltroRequest) -> tuple[list[PerfilRiesgoDataGrid], int]:
        pass

    @abstractmethod
    async def getPerfilById(self, id: str) -> PerfilRiesgo:
        pass

    @abstractmethod
    async def get_dispersion(self, id: str) -> dict:
        pass

    @abstractmethod
    async def cambiar_lista_perfil(self, t: CambiarListaRequest) -> None:
        pass
