from app.core.domain.base_model import Base
from sqlalchemy import Column, String, UUID, TIMESTAMP, Boolean, JSON, Text


class AuditoriaDataGrid(Base):
    __tablename__ = "vw_auditoria"
    __table_args__ = {'extend_existing': True}

    audit_id = Column(UUID(as_uuid=True), primary_key=True)
    entidad_tipo_codigo = Column(String(40))
    entidad_tipo = Column(String(255))
    entidad_id = Column(UUID(as_uuid=True))
    numero_documento = Column(String(50))
    accion_tipo_codigo = Column(String(40))
    accion_tipo = Column(String(255))
    campo_modificado = Column(String(100))
    valor_anterior = Column(Text)
    valor_nuevo = Column(Text)
    usuario_id = Column(UUID(as_uuid=True))
    nombre_usuario = Column(String(500))
    correo = Column(String(100))
    fecha_hora = Column(TIMESTAMP(timezone=False))
    comentario = Column(Text)
    ip_address = Column(String(50))
    datos_adicionales = Column(JSON)
    habilitado = Column(Boolean)
    creado = Column(TIMESTAMP(timezone=False))
