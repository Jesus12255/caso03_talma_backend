from datetime import datetime
from decimal import Decimal
from tokenize import String
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from dto.base_request import BaseRequest
from dto.confianza_extraccion_dtos import GuiaAereaConfianzaRequest
from dto.interviniente_dtos import GuiaAereaIntervinienteRequest, IntervinienteRequest
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


class GuiaAereaIntervinienteResponse(BaseModel):
    guiaAereaIntervinienteId: Optional[UUID] = None
    guiaAereaId: Optional[UUID] = None
    intervinienteId: Optional[UUID] = None
    rolCodigo: Optional[str] = None

    nombre: Optional[str] = None
    confidenceNombre: Optional[float] = None

    direccion: Optional[str] = None
    confidenceDireccion: Optional[float] = None

    ciudad: Optional[str] = None
    confidenceCiudad: Optional[float] = None

    paisCodigo: Optional[str] = None
    confidencePaisCodigo: Optional[float] = None

    telefono: Optional[str] = None
    confidenceTelefono: Optional[float] = None

    tipoDocumentoCodigo: Optional[str] = None
    confidenceTipoDocumentoCodigo: Optional[float] = None

    numeroDocumento: Optional[str] = None
    confidenceNumeroDocumento: Optional[float] = None


    

class GuiaAereaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    guiaAereaId: Optional[str] = None

    numero: Optional[str] = None
    confidenceNumero: Optional[float] = None

    tipoCodigo: Optional[str] = None

    fechaEmision: Optional[datetime] = None
    confidenceFechaEmision: Optional[float] = None

    origenCodigo: Optional[str] = None
    confidenceOrigenCodigo: Optional[float] = None

    destinoCodigo: Optional[str] = None
    confidenceDestinoCodigo: Optional[float] = None

    transbordo: Optional[str] = None
    confidenceTransbordo: Optional[float] = None

    aerolineaCodigo: Optional[str] = None
    confidenceAerolineaCodigo: Optional[float] = None

    numeroVuelo: Optional[str] = None
    confidenceNumeroVuelo: Optional[float] = None

    fechaVuelo: Optional[datetime] = None
    confidenceFechaVuelo: Optional[float] = None

    descripcionMercancia: Optional[str] = None
    confidenceDescripcionMercancia: Optional[float] = None

    cantidadPiezas: Optional[int] = None
    confidenceCantidadPiezas: Optional[float] = None

    pesoBruto: Optional[Decimal] = None
    confidencePesoBruto: Optional[float] = None

    pesoCobrado: Optional[Decimal] = None
    confidencePesoCobrado: Optional[float] = None

    unidadPesoCodigo: Optional[str] = None
    confidenceUnidadPesoCodigo: Optional[float] = None


    volumen: Optional[Decimal] = None
    confidenceVolumen: Optional[float] = None

    naturalezaCargaCodigo: Optional[str] = None
    confidenceNaturalezaCargaCodigo: Optional[float] = None
    
    valorDeclarado: Optional[Decimal] = None
    confidenceValorDeclarado: Optional[float] = None

    tipoFleteCodigo: Optional[str] = None
    confidenceTipoFleteCodigo: Optional[float] = None

    tarifaFlete: Optional[Decimal] = None
    confidenceTarifaFlete: Optional[float] = None

    otrosCargos: Optional[Decimal] = None
    confidenceOtrosCargos: Optional[float] = None

    monedaCodigo: Optional[str] = None
    confidenceMonedaCodigo: Optional[float] = None

    totalFlete: Optional[Decimal] = None
    confidenceTotalFlete: Optional[float] = None

    instruccionesEspeciales: Optional[str] = None
    confidenceInstruccionesEspeciales: Optional[float] = None

    observaciones: Optional[str] = None
    
    confidenceTotal: Optional[float] = None
    
    intervinientesValidos: Optional[List[GuiaAereaIntervinienteResponse]] = Field(default_factory=list)


 



class GuiaAereaSubsanarRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    guiaAereaId: Optional[UUID] = None
    numero: Optional[str] = None
    fechaEmision: Optional[datetime] = None
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
    intervinientes : Optional[List[GuiaAereaIntervinienteRequest]] = Field(default=None)



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
