from dto.audit_dtos import AuditoriaComboResponse
from dto.audit_dtos import AuditoriaDataGridResponse
from fastapi import APIRouter, Depends
from app.core.facade.audit_facade import AuditFacade
from app.core.dependencies.dependencies_audit import get_audit_facade
from dto.audit_dtos import AuditFiltroRequest, AuditResponse, AuditEstadisticasResponse
from dto.collection_response import CollectionResponse


router = APIRouter()

@router.get("/init", response_model=AuditoriaComboResponse)
async def init(audit_facade: AuditFacade = Depends(get_audit_facade)):
    return await audit_facade.init()


@router.post("/find", response_model=CollectionResponse[AuditoriaDataGridResponse])
async def find( request: AuditFiltroRequest, audit_facade: AuditFacade = Depends(get_audit_facade)) -> CollectionResponse[AuditoriaDataGridResponse]:
  return await audit_facade.find(request)


@router.get("/estadisticas", response_model=AuditEstadisticasResponse)
async def get_estadisticas(
    audit_facade: AuditFacade = Depends(get_audit_facade)
) -> AuditEstadisticasResponse:
    """Obtener estadísticas de auditoría"""
    return await audit_facade.obtener_estadisticas()
