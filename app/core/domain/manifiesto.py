from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    TIMESTAMP,
    Numeric,
    Boolean
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import relationship

class Manifiesto(BaseModel):
    __tablename__ = "manifiesto"

    manifiesto_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_vuelo = Column(String(50), nullable=True)
    fecha_vuelo = Column(TIMESTAMP(timezone=False), nullable=True)
    aerolinea_codigo = Column(String(40), nullable=True)
    
    origen_codigo = Column(String(40), nullable=True)
    destino_codigo = Column(String(40), nullable=True)
    
    total_guias = Column(Integer, default=0)
    total_bultos = Column(Integer, default=0)
    peso_bruto_total = Column(Numeric(12, 2), default=0.00)
    volumen_total = Column(Numeric(12, 3), default=0.000)
    
    estado_codigo = Column(String(40), nullable=True)
    
    es_valido = Column(Boolean, default=False)
    errores_validacion = Column(String, nullable=True) # JSON stored as string
    

    # Relationships
    guias = relationship("GuiaAerea", back_populates="manifiesto")
