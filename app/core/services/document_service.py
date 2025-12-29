from abc import ABC, abstractmethod

from dto.guia_aerea_dtos import  GuiaAereaRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentService(ABC):

    @abstractmethod
    async def saveOrUpdate(self, request: GuiaAereaRequest):
        pass

    @abstractmethod
    async def get(self, documentoId: str):
        pass

    @abstractmethod
    async def get_all_documents(self, skip: int = 0, limit: int = 10):
        pass