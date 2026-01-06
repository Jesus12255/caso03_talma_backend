from abc import ABC, abstractmethod

class AnalyzeService(ABC):

    
    @abstractmethod
    @abstractmethod
    async def read_and_validate(self, files: list) -> list:
        pass

    @abstractmethod
    async def process_stream(self, files_data: list):
        pass