from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.base_model import BaseModel


class Catalogo(BaseModel):
    __tablename__ = "catalogo"
    __table_args__ = {"schema": "public"}  # o settings.DB_SCHEMA

    catalogo_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    codigo = Column(String(50), nullable=True)
    nombre = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)
    orden = Column(Integer, nullable=True)
    referencia_codigo = Column(String(50), nullable=True)
    valor1 = Column(String, nullable=True)
    valor2 = Column(String, nullable=True)
    prefijo = Column(String(10), nullable=True)
