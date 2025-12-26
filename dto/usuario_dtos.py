from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

from dto.base_request import BaseRequest
from dto.universal_dto import ComboBaseResponse


class UsuarioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    usuarioId: Optional[str] = None
    rolId: Optional[str] = None
    primerNombre: Optional[str] = None
    segundoNombre: Optional[str] = None
    apellidoPaterno: Optional[str] = None
    apellidoMaterno: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = Field(None, min_length=9, max_length=15)
    tipoDocumentoCodigo: Optional[str] = None
    documento: Optional[str] = None


class UsuarioComboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tipoDocumento: Optional[ComboBaseResponse] = None
    rol: Optional[ComboBaseResponse] = None

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    usuarioId: Optional[str] = None
    rolId: Optional[str] = None
    primerNombre: Optional[str] = None
    segundoNombre: Optional[str] = None
    apellidoPaterno: Optional[str] = None
    apellidoMaterno: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = Field(None, min_length=9, max_length=15)
    tipoDocumentoCodigo: Optional[str] = None
    documento: Optional[str] = None
    combo: Optional[UsuarioComboResponse] = None


class UsuarioFiltroResponse(BaseModel): 
    model_config = ConfigDict(from_attributes=True)
    
    usuarioId: Optional[str] = None
    nombreCompleto: Optional[str] = None
    correo: Optional[str] = None
    celular: Optional[str] = None
    rolCodigo: Optional[str] = None
    rol: Optional[str] = None
    tipoDocumento: Optional[str] = None
    documento: Optional[str] = None
    estado: Optional[str] = None
    creado: Optional[str] = None


class UsuarioStatusRequest(BaseModel):
    usuarioId: str
    habilitado: bool

class UsuarioFiltroRequest(BaseRequest):
    model_config = ConfigDict(from_attributes=True)

    nombre: Optional[str] = None
    rolCodigo: Optional[str] = None
    fechaInicio: Optional[str] = None
    fechaFin: Optional[str] = None
    palabraClave: Optional[str] = None
    habilitado: Optional[bool] = None
