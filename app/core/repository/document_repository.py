from abc import ABC, abstractmethod
from app.core.domain.document import Document


class DocumentRepository(ABC):

    @abstractmethod
    async def save(self, doc: Document) -> Document:
        pass

    @abstractmethod
    async def find_all(self) -> list[Document]:
        pass

    @abstractmethod
    async def find_by_id(self, id) -> Document | None:
        pass

    @abstractmethod
    async def delete(self, id) -> bool:
        pass
