from abc import abstractmethod
from typing import Any, Optional
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from app.integration.base_repository import BaseRepository


class GuiaAereaFiltroRepository(BaseRepository[GuiaAereaDataGrid]):
    
    @abstractmethod
    async def find_data_grid(self, filters: list, start: int, limit: int, sort: Optional[str] = None) -> tuple[Any, int]:
        pass

    @abstractmethod
    async def find_by_ids(self, ids: list[str]) -> list[GuiaAereaDataGrid]:
        pass

    @abstractmethod
    async def find_by_manifiesto_id(self, manifiesto_id: str) -> list[GuiaAereaDataGrid]:
        pass