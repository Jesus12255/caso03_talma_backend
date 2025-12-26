from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.baseModel import Base

class VwUsuario(Base):
    __tablename__ = "vw_usuario"

    usuario_id = Column(UUID(as_uuid=True), primary_key=True)
    rol_id = Column(UUID(as_uuid=True), nullable=True)
    rol_codigo = Column(String, nullable=True)
    rol = Column(String, nullable=True)
    usuario = Column(String, nullable=True)
    nombre_completo = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    celular = Column(String, nullable=True)
    token = Column(String, nullable=True)
    fecha_expiracion_token = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_consulta = Column(String, nullable=True)
    tipo_documento_codigo = Column(String, nullable=True)
    tipo_documento = Column(String, nullable=True)
    documento = Column(String, nullable=True)
    habilitado = Column(Boolean, nullable=True)
