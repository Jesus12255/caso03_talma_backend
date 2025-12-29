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
    intervinientes: List[IntervinienteRequest] = Field(
        ...,
        length=2,
        description="Debe incluir remitente y consignatario"
    )
    numero: str = Field(..., max_length=20)
    tipoCodigo: str = Field(..., max_length=40)
    fechaEmision: datetime
    estadoGuiaCodigo: str = Field(..., max_length=40)
    origenCodigo: str = Field(..., max_length=40)
    destinoCodigo: str = Field(..., max_length=40)
    transbordo: Optional[str] = Field(None, max_length=200)
    aerolineaCodigo: Optional[str] = Field(None, max_length=40)
    numeroVuelo: Optional[str] = Field(None, max_length=50)
    fechaVuelo: Optional[datetime] = None
    descripcionMercancia: Optional[str] = None
    cantidadPiezas: int = Field(..., gt=0)
    pesoBruto: Optional[Decimal] = None
    pesoCobrado: Optional[Decimal] = None
    unidadPesoCodigo: Optional[str] = Field(None, max_length=40)
    volumen: Optional[Decimal] = None
    naturalezaCargaCodigo: Optional[str] = Field(None, max_length=40)
    valorDeclarado: Optional[Decimal] = None
    tipoFleteCodigo: Optional[str] = Field(None, max_length=40)
    tarifaFlete: Optional[Decimal] = None
    otrosCargos: Optional[Decimal] = None
    monedaCodigo: str = Field(..., max_length=40)
    totalFlete: Decimal
    instruccionesEspeciales: Optional[str] = None
    observaciones: Optional[str] = None
    estadoRegistroCodigo: str = Field(..., max_length=40)
    confianzas: List[GuiaAereaConfianzaRequest] = Field(
        ...,
        length=42,
        description="Cada campo debe tener su nivel de confianza correspondiente"
    )
    

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    documentoId: Optional[str] = None
    nombre: Optional[str] = None 
    confiabilidad: Optional[float] = None
    anonimizado: Optional[bool] = None
    datos: Optional[DatoRequest] = None 