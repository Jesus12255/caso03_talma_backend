import json
from typing import AsyncGenerator, List
from fastapi.params import File
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from app.core.facade.analyze_facade import AnalyzeFacade
from app.core.services.analyze_service import AnalyzeService
from utl.file_util import FileUtil


class AnalyzeFacadeImpl(AnalyzeFacade):

    def __init__(self, analyze_service):
        self.analyze_service = analyze_service

    async def upload(self, files: List[UploadFile]) -> StreamingResponse:
        files_data = await self.analyze_service.read_and_validate(files)

        async def event_stream() -> AsyncGenerator[str, None]:
            async for event in self.analyze_service.process_stream(files_data):
                yield self._sse(event)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream"
        )

    @staticmethod
    def _sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"