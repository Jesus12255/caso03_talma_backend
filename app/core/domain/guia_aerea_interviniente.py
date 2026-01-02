from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    ForeignKey,
    Text,
    Float
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Boolean

class GuiaAereaInterviniente(BaseModel):
    __tablename__ = "guia_aerea_interviniente"

    guia_aerea_interviniente_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    guia_aerea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("guia_aerea1.guia_aerea_id"),
        nullable=False
    )
    
    interviniente_id = Column(UUID(as_uuid=True), nullable=True) # Optional link to master Interviniente

    rol_codigo = Column(String(40), nullable=False)

    nombre = Column(String(200), nullable=False)
    confidence_nombre = Column(Float, nullable=True)

    direccion = Column(Text, nullable=True)
    confidence_direccion = Column(Float, nullable=True)

    ciudad = Column(String(200), nullable=True)
    confidence_ciudad = Column(Float, nullable=True)

    pais_codigo = Column(String(40), nullable=True)
    confidence_pais_codigo = Column(Float, nullable=True)

    telefono = Column(String(20), nullable=True)
    confidence_telefono = Column(Float, nullable=True)

    tipo_documento_codigo = Column(String(40), nullable=True)
    confidence_tipo_documento_codigo = Column(Float, nullable=True)

    numero_documento = Column(String(20), nullable=True)
    confidence_numero_documento = Column(Float, nullable=True)

    version = Column(Integer, nullable=False, default=1)
    es_version_activa = Column(Boolean, default=True)
   
    guia_aerea = relationship("GuiaAerea", back_populates="intervinientes")
