from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from app.core.dependencies.dependencies_documento import get_document_facade
from app.core.facade.document_facade import DocumentFacade
from dto.guia_aerea_dtos import GuiaAereaDataGridResponse, GuiaAereaFiltroRequest
from dto.collection_response import CollectionResponse
from dto.universal_dto import BaseOperacionResponse

router = APIRouter()

@router.post("/saveOrUpdate", response_model=BaseOperacionResponse)
async def saveOrUpdate(files: List[UploadFile] = File(...), requestForm: str = Form(...), document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.saveOrUpdate(files, requestForm)


@router.post("/find", response_model=CollectionResponse[GuiaAereaDataGridResponse])
async def find(request: GuiaAereaFiltroRequest, document_facade: DocumentFacade = Depends(get_document_facade)):
    return await document_facade.find(request)

