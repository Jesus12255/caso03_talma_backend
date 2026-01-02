from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.dependencies.dependencies_documento import get_document_facade
from app.core.facade.document_facade import DocumentFacade
from dto.guia_aerea_dtos import GuiaAereaDataGridResponse, GuiaAereaFiltroRequest, GuiaAereaRequest, GuiaAereaResponse
from dto.collection_response import CollectionResponse
from dto.universal_dto import BaseOperacionResponse

router = APIRouter()

@router.get("/get/{guia_aerea_id}", response_model=GuiaAereaResponse)
async def get(guia_aerea_id: str, document_facade: DocumentFacade = Depends(get_document_facade)) -> GuiaAereaResponse:
    return await document_facade.get(guia_aerea_id)

@router.post("/saveOrUpdate", response_model=BaseOperacionResponse)
async def saveOrUpdate(files: List[UploadFile] = File(...), requestForm: str = Form(...), document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.saveOrUpdate(files, requestForm)

@router.post("/find", response_model=CollectionResponse[GuiaAereaDataGridResponse])
async def find(request: GuiaAereaFiltroRequest, document_facade: DocumentFacade = Depends(get_document_facade)):
    return await document_facade.find(request)

@router.post("/update", response_model=BaseOperacionResponse)
async def update(request: GuiaAereaRequest, document_facade: DocumentFacade = Depends(get_document_facade))  -> BaseOperacionResponse:
    return await document_facade.update(request)

@router.post("reprocess/{document_id}", response_model=BaseOperacionResponse)
async def reprocess(document_id: UUID, document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.reprocess(document_id)



