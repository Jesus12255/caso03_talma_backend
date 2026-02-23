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