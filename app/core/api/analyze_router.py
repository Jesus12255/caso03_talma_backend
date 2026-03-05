from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.core.dependencies.dependencies_analyze import get_analyze_facade
from app.core.facade.analyze_facade import AnalyzeFacade
from config.config import settings
from dto.universal_dto import BaseOperacionResponse



router = APIRouter()

@router.post("/upload")
async def upload(
    files: List[UploadFile] = File(...),
    model: str = Form(default=None),
    analyze_facade: AnalyzeFacade = Depends(get_analyze_facade)
) -> BaseOperacionResponse:
    selected_model = model or settings.LLM_MODEL_NAME
    return await analyze_facade.upload(files, selected_model)