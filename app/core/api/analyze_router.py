from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from app.core.dependencies.dependencies_analyze import get_analyze_service
from app.core.services.analyze_service import AnalyzeService


router = APIRouter()

@router.post("/upload")
async def upload(files: List[UploadFile] = File(...), analyze_service: AnalyzeService = Depends(get_analyze_service)):
    files_data = []
    for file in files:
        content = await file.read()
        files_data.append({"filename": file.filename, "content": content})
    
    async def event_stream():
        async for token in analyze_service.upload_stream(files_data):
            yield token
    return StreamingResponse(event_stream(), media_type="text/event-stream")