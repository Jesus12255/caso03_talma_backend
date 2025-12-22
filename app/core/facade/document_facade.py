from abc import ABC, abstractmethod
from typing import List
from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentFacade(ABC):
    
    @abstractmethod
    async def save(self, request: List[DocumentRequest]) -> BaseOperacionResponse:
        pass