from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class IntervinienteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    intervinienteId: Optional[str] = None
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=200)
    paisCodigo: Optional[str] = Field(None, max_length=40)
    telefono: Optional[str] = Field(None, max_length=20)
    tipoDocumentoCodigo: Optional[str] = Field(None, max_length=40)
    numeroDocumento: Optional[str] = Field(None, max_length=20)
    tipoCodigo: Optional[str] = Field(None, max_length=40)

class GuiaAereaIntervinienteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    guiaAereaIntervinienteId: Optional[str] = None
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=200)
    paisCodigo: Optional[str] = Field(None, max_length=40)
    telefono: Optional[str] = Field(None, max_length=20)
    tipoDocumentoCodigo: Optional[str] = Field(None, max_length=40)
    numeroDocumento: Optional[str] = Field(None, max_length=20)
    rolCodigo: Optional[str] = Field(None, max_length=40)
    

