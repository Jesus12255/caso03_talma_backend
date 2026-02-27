from app.integration.base_repository import BaseRepository
from app.core.domain.auditoria_data_grid import AuditoriaDataGrid
from typing import Any
from abc import abstractmethod
from typing import Optional

class AuditFiltroRepository(BaseRepository[AuditoriaDataGrid]):
    
    @abstractmethod
    async def find_data_grid(self, filters: list, start: int, limit: int, sort: Optional[str] = None) -> tuple[Any, int]:
        pass
