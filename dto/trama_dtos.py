from dto.universal_dto import ComboBaseResponse
from dto.base_request import BaseRequest
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class TramaRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    manifiestoIds: List[UUID] = []

class TramaFiltroRequest(BaseRequest):
    model_config = ConfigDict(from_attributes=True)
    
    numeroVuelo: Optional[str] = None
    aerolineaCodigo: Optional[str] = None
    fechaInicioRegistro: Optional[datetime] = None
    fechaFinRegistro: Optional[datetime] = None

class ManifiestoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    manifiestoId: Optional[UUID] = None
    numeroVuelo: Optional[str] = None
    fechaVuelo: Optional[datetime] = None
    aerolineaCodigo: Optional[str] = None
    origenCodigo: Optional[str] = None
    destinoCodigo: Optional[str] = None
    totalGuias: int = 0
    totalBultos: int = 0
    pesoBrutoTotal: Decimal = Decimal(0.00)
    volumenTotal: Decimal = Decimal(0.000)
    estadoCodigo: Optional[str] = None
    esValido: bool = False
    erroresValidacion: Optional[str] = None


class ManifiestoFiltroRequest(BaseRequest):
    model_config = ConfigDict(from_attributes=True)

    numeroVuelo: Optional[str] = None
    fechaInicioVuelo: Optional[datetime] = None
    fechaFinVuelo: Optional[datetime] = None
    aerolineaCodigo: Optional[str] = None
    estadoCodigo: Optional[str] = None





class TramaComboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    estado: Optional[ComboBaseResponse] = None

    