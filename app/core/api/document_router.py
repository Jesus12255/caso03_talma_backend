from typing import List
from fastapi import APIRouter, Depends

from app.core.dependencies.dependencies_document import get_document_facade
from app.core.facade.document_facade import DocumentFacade
from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse

router = APIRouter()

@router.post("/save", response_model=BaseOperacionResponse)
async def save( requestList: List[DocumentRequest], document_facade: DocumentFacade = Depends(get_document_facade)) -> BaseOperacionResponse:
    return await document_facade.save(requestList)