import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.domain.base_model import BaseModel


class ConfianzaExtraccion(BaseModel):
    __tablename__ = "confianza_extraccion1"

    confianza_extraccion_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Polymorphic Foreign Key
    entidad_tipo = Column(String(40), nullable=False)
    entidad_id = Column(UUID(as_uuid=True), nullable=False)

    nombre_campo = Column(String(100), nullable=False)
    
    valor_extraido = Column(Text)
    
    confidence_modelo = Column(Float, nullable=False)

    modelo_codigo = Column(String(50), nullable=True)
    modelo_version = Column(String(20), nullable=True)

    fecha_extraccion = Column(TIMESTAMP(timezone=False), server_default=func.now())
