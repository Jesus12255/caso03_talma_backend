from abc import ABC, abstractmethod
from typing import Any, Dict, List
from fastapi import UploadFile

class AnalyzeService(ABC):

    @abstractmethod
    async def upload(self, t: List[UploadFile]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def upload_stream(self, files_data: List[Dict[str, Any]]):
        pass