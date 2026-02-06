from abc import abstractmethod
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from app.core.domain.manifiesto import Manifiesto
from typing import Optional

class ManifiestoRepository(BaseRepositoryImpl[Manifiesto]):
    
    @abstractmethod
    async def find_by_vuelo_fecha(self, numero_vuelo: str, fecha_vuelo: str) -> Optional[Manifiesto]:
        pass

    @abstractmethod
    async def find(self, filters: list, start: int, limit: int, sort: Optional[str] = None) -> tuple[list[Manifiesto], int]:
        pass

    @abstractmethod
    async def get_with_guias(self, manifiesto_id) -> Optional[Manifiesto]:
        pass