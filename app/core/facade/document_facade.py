from pyasn1.type.univ import Any
from dto.universal_dto import BaseOperacionResponse
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from fastapi import File, Form, UploadFile
from fastapi.responses import StreamingResponse
from dto.guia_aerea_dtos import DescargarGuiaAereaRequest, GuiaAereaComboResponse, GuiaAereaFiltroRequest, GuiaAereaRequest, GuiaAereaResponse, GuiaAereaSubsanarRequest, GuiaAereaDataGridResponse, DeleteAllGuiaAereaRequest




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

    @abstractmethod
    async def get(self, guia_aerea_id: UUID) -> GuiaAereaResponse:
        pass

    @abstractmethod
    def validar_campos_requeridos_guia_aerea(self, guia: GuiaAereaRequest):
        pass

    @abstractmethod
    async def updateAndReprocess(self, request: GuiaAereaSubsanarRequest)  -> BaseOperacionResponse:
        pass

    @abstractmethod
    async def descargarGuiaAerea(self, request: DescargarGuiaAereaRequest) -> StreamingResponse:
        pass

    @abstractmethod
    async def delete(self, guia_aerea_id: UUID) -> BaseOperacionResponse:
        pass

    @abstractmethod
    async def deleteAll(self, request: DeleteAllGuiaAereaRequest) -> BaseOperacionResponse:
        pass