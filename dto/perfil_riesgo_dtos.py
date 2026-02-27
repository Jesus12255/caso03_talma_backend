from dto.universal_dto import ComboBaseResponse
from dto.base_request import BaseRequest
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime   

class PerfilRiesgoDataGridResponse(BaseModel):
    perfilRiesgoId: Optional[UUID] = None
    nombreNormalizado: Optional[str] = None
    tipoIntervinienteCodigo: Optional[str] = None
    tipoInterviniente: Optional[str] = None
    variacionesNombre: Optional[List[Any]] = None
    telefonosConocidos: Optional[List[Any]] = None
    direccionesConocidas: Optional[List[Any]] = None
    pesoPromedio: Optional[float] = None
    pesoStdDev: Optional[float] = None
    pesoMaximoHistorico: Optional[float] = None
    pesoMinimoHistorico: Optional[float] = None
    cantidadEnvios: Optional[int] = None
    diasPromedioEntreEnvios: Optional[int] = None
    fechaPrimerEnvio: Optional[datetime] = None
    fechaUltimoEnvio: Optional[datetime] = None
    rutasFrecuentes: Optional[Dict[str, Any]] = None
    totalConsignatariosVinculados: Optional[int] = None
    scoreBase: Optional[int] = None
    factorTolerancia: Optional[float] = None
    creado: Optional[datetime] = None
    habilitado: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class PerfilRiesgoFiltroRequest(BaseRequest):
    perfilRiesgoId: Optional[str] = None
    nombreNormalizado: Optional[str] = None
    tipoIntervinienteCodigo: Optional[str] = None
    cantidadEnviosMaximo: Optional[int] = None
    cantidadEnviosMinimo: Optional[int] = None
    fechaFin: Optional[datetime] = None
    fechaInicio: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class PerfilRiesgoComboResponse(BaseModel):
    tipoInterviniente: Optional[ComboBaseResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PerfilRiesgoResponse(BaseModel):
    perfilRiesgoId: Optional[UUID] = None
    nombreNormalizado: Optional[str] = None
    tipoIntervinienteCodigo: Optional[str] = None
    
    variacionesNombre: Optional[List[Any]] = None
    telefonosConocidos: Optional[List[Any]] = None
    direccionesConocidas: Optional[List[Any]] = None
    
    pesoPromedio: Optional[float] = None
    pesoStdDev: Optional[float] = None
    pesoMaximoHistorico: Optional[float] = None
    pesoMinimoHistorico: Optional[float] = None
    
    cantidadEnvios: Optional[int] = None
    diasPromedioEntreEnvios: Optional[int] = None
    fechaPrimerEnvio: Optional[datetime] = None
    fechaUltimoEnvio: Optional[datetime] = None
    esPerfilDurmiente: Optional[bool] = None
    
    rutasFrecuentes: Optional[Dict[str, Any]] = None
    totalConsignatariosVinculados: Optional[int] = None
    
    scoreBase: Optional[int] = None
    totalAlertasGeneradas: Optional[int] = None
    totalAlertasConfirmadas: Optional[int] = None
    factorTolerancia: Optional[float] = None

    creado: Optional[datetime] = None
    habilitado: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class DatapointDispersion(BaseModel):
    fecha: datetime
    peso: float

class PerfilRiesgoDispersionResponse(BaseModel):
    pesoPromedio: Optional[float] = 0.0
    pesoStdDev: Optional[float] = 0.0
    puntos: Optional[List[DatapointDispersion]] = []
    
    model_config = ConfigDict(from_attributes=True)

class GrafoNodo(BaseModel):
    id: str  # IATA o Interviniente ID
    name: str # Nombre ciudad o Nombre Interviniente
    lat: float
    lng: float
    type: str # 'airport', 'sender', 'consignee'
    size: float
    color: str
    
class GrafoArco(BaseModel):
    id: Optional[str] = None # AWB ID or Number
    startLat: float
    startLng: float
    endLat: float
    endLng: float
    color: str
    label: str
    sender: Optional[str] = None
    consignee: Optional[str] = None
    altitude: Optional[float] = 0.2
    stroke: Optional[float] = 1.0

class RedVinculosResponse(BaseModel):
    nodes: List[GrafoNodo] = []
    arcs: List[GrafoArco] = []
    
    model_config = ConfigDict(from_attributes=True)

class CambiarListaRequest(BaseModel):
    perfil_riesgo_id: UUID
    nueva_lista: str 
