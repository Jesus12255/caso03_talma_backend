from abc import ABC, abstractmethod
from typing import AsyncGenerator

class StorageService(ABC):
    
    @abstractmethod
    async def upload_file(self, filename: str, content: bytes, content_type: str) -> str:
        pass

    @abstractmethod
    async def download_file_stream(self, url: str) -> AsyncGenerator[bytes, None]:
        pass
