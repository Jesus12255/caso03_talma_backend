from dto.audit_dtos import AuditoriaComboResponse
from abc import ABC
from abc import abstractmethod
from dto.audit_dtos import AuditFiltroRequest, AuditResponse, AuditEstadisticasResponse
from dto.collection_response import CollectionResponse


class AuditFacade(ABC):

    @abstractmethod
    async def init(self) -> AuditoriaComboResponse:
        pass

    @abstractmethod
    async def find(self, request: AuditFiltroRequest) -> CollectionResponse[AuditResponse]:
        pass
    
    @abstractmethod
    async def obtener_estadisticas(self) -> AuditEstadisticasResponse:
        pass
