
from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.domain.base_model import BaseModel



class Rol(BaseModel):
    __tablename__ = "rol"

    rol_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(50), nullable=True)
    nombre = Column(String(100), nullable=True)
    descripcion = Column(String(200), nullable=True)
    
    usuarios = relationship("Usuario", back_populates="rol")