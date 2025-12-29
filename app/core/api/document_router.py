from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.dependencies.dependencies_documento import get_document_facade
from app.core.facade.document_facade import DocumentFacade
from dto.guia_aerea_dtos import  DocumentResponse
from dto.universal_dto import BaseOperacionResponse

router = APIRouter()

@router.post("/saveOrUpdate", response_model=BaseOperacionResponse)
async def saveOrUpdate(files: List[UploadFile] = File(...), requestForm: str = Form(...), document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.saveOrUpdate(files, requestForm)




@router.get("/", response_model=List[DocumentResponse])
async def get_documents(skip: int = 0, limit: int = 10, document_facade: DocumentFacade = Depends(get_document_facade)):
    return await document_facade.get_all_documents(skip, limit)