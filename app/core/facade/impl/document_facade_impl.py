from typing import List
from app.core.facade.document_facade import DocumentFacade
from app.core.services.document_service import DocumentService
from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentFacadeImpl(DocumentFacade):

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def save(self, t: List[DocumentRequest]) -> BaseOperacionResponse:
        try:
            for tt in t:
                await self.document_service.save(tt)
            return BaseOperacionResponse(codigo="200", mensaje="Documentos guardados correctamente")
        except Exception as e:
            print(f"DEBUG: Error in facade save: {e}")
            return BaseOperacionResponse(codigo="500", mensaje=f"Error al guardar documentos: {e}")