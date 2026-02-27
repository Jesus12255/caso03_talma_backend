from dto.audit_dtos import AuditoriaDataGridResponse
from abc import abstractmethod
from abc import ABC
from typing import List, Optional
from dto.audit_dtos import AuditFiltroRequest


class AuditService(ABC):
    
    @abstractmethod
    async def registrar_creacion(
        self,
        entidad_tipo: str,
        entidad_id: str,
        numero_documento: str,
        metadata: Optional[dict] = None
    ):
        pass
    
    @abstractmethod
    async def registrar_modificacion(
        self,
        entidad_tipo: str,
        entidad_id: str,
        numero_documento: str,
        campo: str,
        valor_anterior: any,
        valor_nuevo: any,
        usuario_id: str,
        comentario: Optional[str] = None
    ):
        pass
    
   
    
    @abstractmethod
    async def find(self, request: AuditFiltroRequest) -> tuple[List[AuditoriaDataGridResponse], int]:
        pass