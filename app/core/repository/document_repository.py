from abc import  abstractmethod
from typing import Optional, List
from app.integration.base_repository import BaseRepository
from app.core.domain.guia_aerea import GuiaAerea

class DocumentRepository(BaseRepository[GuiaAerea]):
    
    @abstractmethod
    async def find_by_numero(self, numero: str, exclude_id: Optional[str] = None) -> Optional[GuiaAerea]:
        pass

    @abstractmethod
    async def get_by_id_with_relations(self, id: str) -> Optional[GuiaAerea]:
        pass

    @abstractmethod
    async def find_recent_by_consignee_names(self, nombres: List[str], hours: int = 24) -> List[GuiaAerea]:
        """Finds recent shipments for any of the given consignee names within the last X hours."""
        pass

    @abstractmethod
    async def count_unique_consignees_for_sender(self, sender_names: List[str]) -> int:
        """Counts unique consignees linked to any of the provided sender names."""
        pass

    