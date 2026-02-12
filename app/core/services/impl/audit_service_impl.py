from app.core.domain.auditoria_data_grid import AuditoriaDataGrid
from dto.audit_dtos import AuditoriaDataGridResponse
from app.core.repository.audit_filtro_repository import AuditFiltroRepository
from typing import List, Optional
from uuid import UUID
from app.core.services.audit_service import AuditService
from app.core.repository.audit_repository import AuditRepository
from app.core.domain.audit import Audit
from dto.audit_dtos import AuditFiltroRequest
from utl.date_util import DateUtil
from utl.constantes import Constantes
from core.service.service_base import ServiceBase



class AuditServiceImpl(AuditService, ServiceBase):
    
    def __init__(self, audit_repository: AuditRepository, audit_filtro_repository: AuditFiltroRepository):
        self.audit_repository = audit_repository
        self.audit_filtro_repository = audit_filtro_repository
    
    async def registrar_creacion(
        self,
        entidad_tipo: str,
        entidad_id: UUID,
        numero_documento: str,
        metadata: Optional[dict] = None
    ) -> None:
        audit = Audit()
        audit.entidad_tipo_codigo = entidad_tipo
        audit.entidad_id = entidad_id
        audit.numero_documento = numero_documento
        audit.accion_tipo_codigo = Constantes.TipoAccionAuditoria.CREADO
        audit.usuario_id = self.session.user_id
        audit.fecha_hora = DateUtil.get_current_local_datetime()
        audit.ip_address = self.session.ip_address
        audit.datos_adicionales = metadata
        audit.habilitado = Constantes.HABILITADO
        audit.creado = DateUtil.get_current_local_datetime()
        audit.creado_por = Constantes.SYSTEM_USER
        await self.audit_repository.save(audit)
    
    async def registrar_modificacion(
        self,
        entidad_tipo: str,
        entidad_id: UUID,
        numero_documento: str,
        campo: str,
        valor_anterior: any,
        valor_nuevo: any,
        comentario: Optional[str] = None
    ) -> None:
        try:
            audit = Audit()
            audit.entidad_tipo_codigo = entidad_tipo
            audit.entidad_id = entidad_id
            audit.numero_documento = numero_documento
            audit.accion_tipo_codigo = Constantes.TipoAccionAuditoria.MODIFICADO
            audit.campo_modificado = campo
            audit.valor_anterior = valor_anterior
            audit.valor_nuevo = valor_nuevo
            audit.usuario_id = UUID(self.session.user_id) if self.session and self.session.user_id else None
            audit.fecha_hora = DateUtil.get_current_local_datetime()
            audit.ip_address = self.session.ip_address if self.session and self.session.ip_address else None
            audit.comentario = comentario
            audit.habilitado = Constantes.HABILITADO
            audit.creado = DateUtil.get_current_local_datetime()
            audit.creado_por = Constantes.SYSTEM_USER
            await self.audit_repository.save(audit)
        except Exception as e:
            logger.error(f"ERROR CRÍTICO AL GUARDAR AUDITORÍA MODIFICACIÓN: {e}")
            logger.error(f"Detalles: Entidad={entidad_tipo}, ID={entidad_id}")
  
    
    
    
    async def find(self, request: AuditFiltroRequest) -> tuple[List[AuditoriaDataGridResponse], int]:
        filters = []
        if request.entidadTipoCodigo:
            filters.append(AuditoriaDataGrid.entidad_tipo_codigo == request.entidadTipoCodigo)
        if request.numeroDocumento:
            filters.append(AuditoriaDataGrid.numero_documento.ilike(f"%{request.numeroDocumento.upper()}%"))
        if request.accionTipoCodigo:
            filters.append(AuditoriaDataGrid.accion_tipo_codigo == request.accionTipoCodigo)
        if request.usuarioId:
            filters.append(AuditoriaDataGrid.usuario_id == request.usuarioId)
        if request.fechaDesde:
            from datetime import datetime
            fecha_desde_dt = datetime.fromisoformat(request.fechaDesde + "T00:00:00")
            filters.append(AuditoriaDataGrid.fecha_hora >= fecha_desde_dt)
        if request.fechaHasta:
            from datetime import datetime
            fecha_hasta_dt = datetime.fromisoformat(request.fechaHasta + "T23:59:59")
            filters.append(AuditoriaDataGrid.fecha_hora <= fecha_hasta_dt)

        data, total_count = await self.audit_filtro_repository.find_data_grid(
            filters=filters,
            start=request.start,
            limit=request.limit,
            sort=request.sort
        )
        return data, total_count