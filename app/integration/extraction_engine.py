from abc import ABC, abstractmethod


class ExtractionEngine(ABC):

    @abstractmethod
    async def extract_stream(self, base64_images: list[str]) -> dict:
        pass