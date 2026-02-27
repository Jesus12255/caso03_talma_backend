
from abc import abstractmethod
from app.core.domain.perfil_riesgo_data_grid import PerfilRiesgoDataGrid
from app.integration.base_repository import BaseRepository
from pyasn1.type.univ import Any
from typing import Optional

class PerfilRiesgoFiltroRepository(BaseRepository[PerfilRiesgoDataGrid]):
    
    @abstractmethod
    async def find_data_grid(self, filters: list, start: int, limit: int, sort: Optional[str] = None) -> tuple[Any, int]:
        pass
