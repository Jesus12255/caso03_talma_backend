from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from app.core.dependencies.dependencies_analyze import get_analyze_facade
from app.core.facade.analyze_facade import AnalyzeFacade
from dto.universal_dto import BaseOperacionResponse



router = APIRouter()

@router.post("/upload")
async def upload(files: List[UploadFile] = File(...), analyze_facade: AnalyzeFacade = Depends(get_analyze_facade)) -> BaseOperacionResponse:
    return await analyze_facade.upload(files)