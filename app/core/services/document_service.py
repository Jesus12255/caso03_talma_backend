from dto.guia_aerea_dtos import DeleteAllGuiaAereaRequest
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID
from app.core.domain.guia_aerea import GuiaAerea
from dto.guia_aerea_dtos import  GuiaAereaFiltroRequest, GuiaAereaRequest, GuiaAereaSubsanarRequest


class DocumentService(ABC):

    @abstractmethod
    async def saveOrUpdate(self, request: GuiaAereaRequest):
        pass

    @abstractmethod
    async def get(self, documentoId: str) -> GuiaAerea:
        pass

    @abstractmethod
    async def find(self, request: GuiaAereaFiltroRequest) -> tuple[Any, int]:
        pass

    @abstractmethod
    async def get_with_relations(self, documentoId: str) -> GuiaAerea:
        pass

    @abstractmethod
    async def reprocess(self, document_id: str):
        pass

    @abstractmethod
    async def updateAndReprocess(self, request: GuiaAereaSubsanarRequest):
        pass

    @abstractmethod
    async def delete(self, guia_aerea_id: UUID) -> bool:
        pass

    @abstractmethod
    async def deleteAll(self, request: DeleteAllGuiaAereaRequest):
        pass