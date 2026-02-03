from dto.guia_aerea_dtos import DeleteAllGuiaAereaRequest
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.core.dependencies.dependencies_documento import get_document_facade
from app.core.facade.document_facade import DocumentFacade
from dto.guia_aerea_dtos import DescargarGuiaAereaRequest, GuiaAereaDataGridResponse, GuiaAereaFiltroRequest, GuiaAereaRequest, GuiaAereaResponse, GuiaAereaSubsanarRequest
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

@router.post("/updateAndReprocess", response_model=BaseOperacionResponse)
async def updateAndReprocess(request: GuiaAereaSubsanarRequest, document_facade: DocumentFacade = Depends(get_document_facade))  -> BaseOperacionResponse:
    return await document_facade.updateAndReprocess(request)

@router.post("/descargarGuiaAerea")
async def descargarGuiaAerea(request: DescargarGuiaAereaRequest, document_facade: DocumentFacade = Depends(get_document_facade)) -> StreamingResponse:
    return await document_facade.descargarGuiaAerea(request)

@router.delete("/delete/{guia_aerea_id}", response_model=BaseOperacionResponse)
async def delete(guia_aerea_id: UUID, document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.delete(guia_aerea_id)

@router.post("/deleteAll", response_model=BaseOperacionResponse)
async def deleteAll(request: DeleteAllGuiaAereaRequest, document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.deleteAll(request)