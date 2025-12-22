from abc import ABC, abstractmethod

from dto.document import DocumentRequest
from dto.universal_dto import BaseOperacionResponse


class DocumentService(ABC):

    @abstractmethod
    async def save(self, request: DocumentRequest):
        pass