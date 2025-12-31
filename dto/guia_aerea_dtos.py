from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from dto.base_request import BaseRequest
from dto.confianza_extraccion_dtos import GuiaAereaConfianzaRequest
from dto.interviniente_dtos import IntervinienteRequest
from dto.universal_dto import ComboBaseResponse

class DatoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    value: str
    
    
class GuiaAereaRequest(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    guiaAereaId: Optional[UUID] = None

    intervinientes: Optional[List[IntervinienteRequest]] = Field(
        default=None,
        description="Debe incluir remitente y consignatario"
    )

    numero: Optional[str] = Field(default=None, max_length=20)
    tipoCodigo: Optional[str] = Field(default=None, max_length=40)
    fechaEmision: Optional[datetime] = None
    estadoGuiaCodigo: Optional[str] = Field(default=None, max_length=40)
    origenCodigo: Optional[str] = Field(default=None, max_length=40)
    destinoCodigo: Optional[str] = Field(default=None, max_length=40)

    transbordo: Optional[str] = Field(default=None, max_length=200)
    aerolineaCodigo: Optional[str] = Field(default=None, max_length=40)
    numeroVuelo: Optional[str] = Field(default=None, max_length=50)
    fechaVuelo: Optional[datetime] = None

    descripcionMercancia: Optional[str] = None
    cantidadPiezas: Optional[int] = Field(default=None, gt=0)

    pesoBruto: Optional[Decimal] = None
    pesoCobrado: Optional[Decimal] = None
    unidadPesoCodigo: Optional[str] = Field(default=None, max_length=40)
    volumen: Optional[Decimal] = None

    naturalezaCargaCodigo: Optional[str] = Field(default=None, max_length=40)
    valorDeclarado: Optional[Decimal] = None
    tipoFleteCodigo: Optional[str] = Field(default=None, max_length=40)
    tarifaFlete: Optional[Decimal] = None
    otrosCargos: Optional[Decimal] = None

    monedaCodigo: Optional[str] = Field(default=None, max_length=40)
    totalFlete: Optional[Decimal] = None

    instruccionesEspeciales: Optional[str] = None
    observaciones: Optional[str] = None
    estadoRegistroCodigo: Optional[str] = Field(default=None, max_length=40)

    confianzas: Optional[List[GuiaAereaConfianzaRequest]] = Field(
        default=None,
        description="Cada campo debe tener su nivel de confianza correspondiente"
    )

class GuiaAereaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    documentoId: Optional[str] = None
    nombre: Optional[str] = None 
    confiabilidad: Optional[float] = None
    anonimizado: Optional[bool] = None
    datos: Optional[DatoRequest] = None 


class GuiaAereaDataGridResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guiaAereaId: Optional[UUID] = None
    remitenteId: Optional[UUID] = None
    nombreRemitente: Optional[str] = None
    direccionRemitente: Optional[str] = None
    telefonoRemitente: Optional[str] = None
    consignatarioId: Optional[UUID] = None
    nombreConsignatario: Optional[str] = None
    direccionConsignatario: Optional[str] = None
    telefonoConsignatario: Optional[str] = None
    numero: Optional[str] = None
    tipoCodigo: Optional[str] = None
    tipo: Optional[str] = None
    fechaEmision: Optional[datetime] = None
    estadoGuiaCodigo: Optional[str] = None
    origenCodigo: Optional[str] = None
    destinoCodigo: Optional[str] = None
    transbordo: Optional[str] = None
    aerolineaCodigo: Optional[str] = None
    numeroVuelo: Optional[str] = None
    fechaVuelo: Optional[datetime] = None
    descripcionMercancia: Optional[str] = None
    cantidadPiezas: Optional[int] = None
    pesoBruto: Optional[Decimal] = None
    pesoCobrado: Optional[Decimal] = None
    unidadPesoCodigo: Optional[str] = None
    volumen: Optional[Decimal] = None
    naturalezaCargaCodigo: Optional[str] = None
    valorDeclarado: Optional[Decimal] = None
    tipoFleteCodigo: Optional[str] = None
    tarifaFlete: Optional[Decimal] = None
    otrosCargos: Optional[Decimal] = None
    monedaCodigo: Optional[str] = None
    totalFlete: Optional[Decimal] = None
    instruccionesEspeciales: Optional[str] = None
    observaciones: Optional[str] = None
    estadoRegistroCodigo: Optional[str] = None
    confidenceTotalPct: Optional[str] = None
    estadoConfianzaCodigo: Optional[str] = None
    estadoConfianza: Optional[str] = None
    estadoRegistro: Optional[str] = None
    habilitado: Optional[bool] = None
    fechaConsulta: Optional[datetime] = None


class GuiaAereaFiltroRequest(BaseRequest):
    model_config = ConfigDict(from_attributes=True)

    estadoRegistroCodigo: Optional[str] = None
    numero: Optional[str] = None
    origenCodigo: Optional[str] = None
    destinoCodigo: Optional[str] = None
    transbordo: Optional[str] = None
    nombreRemitente: Optional[str] = None
    nombreConsignatario: Optional[str] = None
    habilitado: Optional[bool] = None
    fechaInicioRegistro: Optional[datetime] = None
    fechaFinRegistro: Optional[datetime] = None
    vistaCodigo: Optional[str] = None


class GuiaAereaComboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    estado: Optional[ComboBaseResponse] = None
