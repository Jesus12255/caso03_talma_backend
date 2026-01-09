
from sqlalchemy import Column, String, Boolean, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import  relationship
import uuid
from app.core.domain.base_model import BaseModel

class Usuario(BaseModel):
    __tablename__ = "usuario"

    usuario_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol_id = Column(UUID(as_uuid=True), ForeignKey("rol.rol_id"), nullable=True)

    usuario = Column(String, nullable=True)
    password = Column(String, nullable=True)
    primer_nombre = Column(String, nullable=True)
    segundo_nombre = Column(String, nullable=True)
    apellido_paterno = Column(String, nullable=True)
    apellido_materno = Column(String, nullable=True)
    tipo_documento_codigo = Column(String, nullable=True)
    documento = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    celular = Column(String, nullable=True)
    token = Column(String, nullable=True)
  
    rol = relationship("Rol", back_populates="usuarios")

