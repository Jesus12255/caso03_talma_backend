from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import relationship
from app.security.domain.Usuario import Usuario
from app.core.domain.guia_aerea import GuiaAerea

class Notificacion(BaseModel):
    __tablename__ = "notificacion"

    notificacion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.usuario_id"), nullable=True)
    guia_aerea_id = Column(UUID(as_uuid=True), ForeignKey("guia_aerea1.guia_aerea_id"), nullable=True)
    
    tipo_codigo = Column(String(40), nullable=True)
    titulo = Column(String(100), nullable=True)
    mensaje = Column(String(200), nullable=True)
    
    severidad_codigo = Column(String(40), nullable=True)
    estado_codigo = Column(String(40), nullable=True)
    
    meta_data = Column("metadata", JSONB, nullable=True)
    
    leido_en = Column(TIMESTAMP(timezone=False), nullable=True)
    resuelto_en = Column(TIMESTAMP(timezone=False), nullable=True)

    usuario = relationship("Usuario", backref="notificaciones")
    guia_aerea = relationship("GuiaAerea", backref="notificaciones")
