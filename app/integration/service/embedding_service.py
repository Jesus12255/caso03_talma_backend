from abc import ABC, abstractmethod

class EmbeddingService(ABC):
    
    @abstractmethod
    async def get_embedding(self, text: str) -> list[float]:
        """
        Generates a vector embedding for the given text.
        """
        pass
