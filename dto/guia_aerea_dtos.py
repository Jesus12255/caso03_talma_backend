from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from dto.confianza_extraccion_dtos import GuiaAereaConfianzaRequest
from dto.interviniente_dtos import IntervinienteRequest

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

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    documentoId: Optional[str] = None
    nombre: Optional[str] = None 
    confiabilidad: Optional[float] = None
    anonimizado: Optional[bool] = None
    datos: Optional[DatoRequest] = None 