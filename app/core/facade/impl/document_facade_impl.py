import json
import logging
from typing import List

from fastapi import Form, UploadFile
from fastapi.params import File
from app.core.facade.document_facade import DocumentFacade
from app.core.services.document_service import DocumentService
from core.exceptions import AppBaseException
from dto.guia_aerea_dtos import GuiaAereaRequest
from dto.universal_dto import BaseOperacionResponse
from utl.generic_util import GenericUtil

logger = logging.getLogger(__name__)

class DocumentFacadeImpl(DocumentFacade):

    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def saveOrUpdate(self, files: List[UploadFile] = File(...), requestForm: str = Form(...)) -> BaseOperacionResponse:
        try:
            request = json.loads(requestForm)
            if GenericUtil.is_empty_list(request):
                raise ValueError("Debe de enviar al menos un documento en el request")

            for tt in request:
                obj_req = GuiaAereaRequest.model_validate(tt)
                await self.document_service.saveOrUpdate(obj_req)
                
            return BaseOperacionResponse(codigo="200", mensaje="Documentos guardados correctamente")
        except Exception as e:
            logger.error(f"Error al guardar documentos: {e}")
            raise AppBaseException(message="Error al guardar documentos")


    async def get_all_documents(self, skip: int = 0, limit: int = 10):
        return await self.document_service.get_all_documents(skip, limit)