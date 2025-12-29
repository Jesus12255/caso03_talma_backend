from abc import ABC, abstractmethod
from typing import List

from fastapi import File, Form, UploadFile
from dto.universal_dto import BaseOperacionResponse


class DocumentFacade(ABC):
    
    @abstractmethod
    async def saveOrUpdate(self, files: List[UploadFile] = File(...), requestForm: str = Form(...)) -> BaseOperacionResponse:
        pass

    @abstractmethod
    async def get_all_documents(self, skip: int = 0, limit: int = 10):
        pass