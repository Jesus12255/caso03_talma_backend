from abc import abstractmethod
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from typing import Protocol, List, Optional
from datetime import datetime
from app.core.domain.audit import Audit


class AuditRepository(BaseRepositoryImpl[Audit]):
  
    @abstractmethod
    async def find_by_entidad(
        self,
        entidad_tipo: str,
        entidad_id: str,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        usuario_id: Optional[str] = None,
        accion_tipo: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Audit]:
        pass
