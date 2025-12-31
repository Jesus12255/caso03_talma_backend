from abc import ABC, abstractmethod
from typing import List, Any

from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from dto.guia_aerea_dtos import  GuiaAereaFiltroRequest, GuiaAereaRequest


class DocumentService(ABC):

    @abstractmethod
    async def saveOrUpdate(self, request: GuiaAereaRequest):
        pass

    @abstractmethod
    async def get(self, documentoId: str):
        pass

    @abstractmethod
    async def find(self, request: GuiaAereaFiltroRequest) -> tuple[Any, int]:
        pass