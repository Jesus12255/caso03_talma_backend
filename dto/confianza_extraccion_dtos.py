from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GuiaAereaConfianzaRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    confianzaExtraccionId: Optional[UUID] = None
    guiaAereaId: Optional[UUID] = None
    intervinienteId: Optional[UUID] = None
    nombreCampo: str = Field(..., max_length=100)
    valorExtraido: Optional[str] = None
    valorFinal: Optional[str] = None
    confidenceModelo: float = Field(..., ge=0, le=1)
    confidenceFinal: Optional[float] = Field(None, ge=0, le=1)
    corregidoManual: Optional[bool] = None
    validado: Optional[bool] = None




