from dto.universal_dto import ComboBaseResponse
from dto.base_request import BaseRequest
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AuditFiltroRequest(BaseRequest):
    entidadTipoCodigo: Optional[str] = None
    numeroDocumento: Optional[str] = None
    accionTipoCodigo: Optional[str] = None
    usuarioId: Optional[str] = None
    fechaDesde: Optional[str] = None
    fechaHasta: Optional[str] = None
    


class AuditResponse(BaseModel):
    auditId: str
    entidadTipo: str
    entidadId: str
    numeroDocumento: Optional[str]
    accionTipo: str
    campoModificado: Optional[str]
    valorAnterior: Optional[str]
    valorNuevo: Optional[str]
    usuarioNombre: str
    usuarioId: str
    fechaHora: str
    comentario: Optional[str]
    ipAddress: Optional[str]
    datosAdicionales: Optional[dict]


class AuditEstadisticasResponse(BaseModel):
    totalRegistros: int
    registrosPorAccion: dict
    registrosPorEntidad: dict
    usuariosMasActivos: List[dict]


class AuditoriaDataGridResponse(BaseModel):
    auditId: str
    entidadTipoCodigo: str
    entidadTipo: Optional[str] = None
    entidadId: str
    numeroDocumento: Optional[str] = None
    accionTipoCodigo: str
    accionTipo: Optional[str] = None
    campoModificado: Optional[str] = None
    valorAnterior: Optional[str] = None
    valorNuevo: Optional[str] = None
    usuarioId: Optional[str] = None
    nombreUsuario: Optional[str] = None
    correo: Optional[str] = None
    fechaHora: datetime
    comentario: Optional[str] = None
    ipAddress: Optional[str] = None
    datosAdicionales: Optional[dict] = None
    habilitado: bool
    creado: datetime

class AuditoriaComboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accionTipo: Optional[ComboBaseResponse] = None
    entidadTipo: Optional[ComboBaseResponse] = None