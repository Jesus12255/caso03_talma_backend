from abc import ABC, abstractmethod
from typing import List
from fastapi import  UploadFile
from fastapi.responses import StreamingResponse

from dto.guia_aerea_dtos import GuiaAereaRequest


class AnalyzeFacade(ABC):
    
    @abstractmethod
    async def upload(self, files: List[UploadFile]) -> StreamingResponse:
        pass
    
