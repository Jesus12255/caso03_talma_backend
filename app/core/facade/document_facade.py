from abc import ABC, abstractmethod
from typing import List, Any
from uuid import UUID
from fastapi import File, Form, UploadFile
from dto.guia_aerea_dtos import GuiaAereaComboResponse,  GuiaAereaFiltroRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentFacade(ABC):
    
    @abstractmethod
    async def saveOrUpdate(self, files: List[UploadFile] = File(...), requestForm: str = Form(...)) -> BaseOperacionResponse:
        pass

    @abstractmethod
    async def find(self, request: GuiaAereaFiltroRequest) -> Any:
        pass

    @abstractmethod
    async def init(self) -> GuiaAereaComboResponse:
        pass

    @abstractmethod
    async def reprocess(self, document_id: UUID) -> BaseOperacionResponse:
        pass