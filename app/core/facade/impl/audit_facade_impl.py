from utl.constantes import Catalogo
from app.configuration.facade.comun_facade import ComunFacade
from dto.audit_dtos import AuditoriaComboResponse
from config.mapper import Mapper
from dto.audit_dtos import AuditoriaDataGridResponse
from app.core.facade.audit_facade import AuditFacade
from app.core.services.audit_service import AuditService
from dto.audit_dtos import AuditFiltroRequest, AuditEstadisticasResponse
from dto.collection_response import CollectionResponse
from core.facade.facade_base import FacadeBase


class AuditFacadeImpl(AuditFacade, FacadeBase):
    
    def __init__(self, audit_service: AuditService, comun_facade: ComunFacade):
        self.audit_service = audit_service
        self.comun_facade = comun_facade
    

    async def init(self) -> AuditoriaComboResponse:
        return AuditoriaComboResponse(
            accionTipo = await self.comun_facade.load_by_referencia_nombre(Catalogo.ACCION_AUDITORIA),
            entidadTipo = await self.comun_facade.load_by_referencia_nombre(Catalogo.TIPO_ENTIDAD_AUDITORIA)
        )

    async def find( self, request: AuditFiltroRequest) -> CollectionResponse[AuditoriaDataGridResponse]:
        data, total_count = await self.audit_service.find(request)
        elements = [Mapper.to_dto(x, AuditoriaDataGridResponse) for x in data]
        return CollectionResponse[AuditoriaDataGridResponse](
            elements=elements,
            totalCount=total_count,
            start=request.start,
            limit=request.limit
        )
    
    async def obtener_estadisticas(
        self
    ) -> AuditEstadisticasResponse:
        # TODO: Implementar lógica de estadísticas
        # Por ahora retorna datos dummy
        return AuditEstadisticasResponse(
            totalRegistros=0,
            registrosPorAccion={},
            registrosPorEntidad={},
            usuariosMasActivos=[]
        )
