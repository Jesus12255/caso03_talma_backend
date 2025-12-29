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
    __tablename__ = "confianza_extraccion"

    confianza_extraccion_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    guia_aerea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("guia_aerea.guia_aerea_id"),
        nullable=True
    )

    interviniente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviniente.interviniente_id"),
        nullable=True
    )

    nombre_campo = Column(String(100), nullable=False)

    valor_extraido = Column(Text)
    valor_final = Column(Text)

    confidence_modelo = Column(Float, nullable=False)
    confidence_final = Column(Float, nullable=False)

    corregido_manual = Column(Boolean, default=False)
    validado = Column(Boolean, default=False)

    guia_aerea = relationship(
        "GuiaAerea",
        back_populates="confianzas_extraccion"
    )

    interviniente = relationship(
        "Interviniente",
        back_populates="confianzas_extraccion"
    )
