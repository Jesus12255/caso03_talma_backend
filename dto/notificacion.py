from uuid import UUID
from pydantic import BaseModel, ConfigDict

class NotificacionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    notificacionId: UUID
    guiaAereaId: UUID
    usuarioId: UUID
    tipoCodigo: str
    titulo: str
    mensaje: str
    severidadCodigo: str
    
    
    
from datetime import datetime

class NotificacionResponse(NotificacionRequest):
    estadoCodigo: str
    creado: datetime
    metaData: dict | None = None