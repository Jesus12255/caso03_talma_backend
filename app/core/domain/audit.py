from sqlalchemy import true
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import relationship


class Audit(BaseModel):
    __tablename__ = "audit"

    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
   
    entidad_tipo_codigo = Column(String(40), nullable=True, index=True) 
    entidad_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    numero_documento = Column(String(50), nullable=True, index=True) 
    
  
    accion_tipo_codigo = Column(String(40), nullable=True) 
    campo_modificado = Column(String(100), nullable=True)  
    
    
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.usuario_id"), nullable=True, index=True)
    fecha_hora = Column(TIMESTAMP(timezone=False), nullable=True, index=True)
    comentario = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    datos_adicionales = Column(JSON, nullable=True)
    
    usuario = relationship("Usuario")
