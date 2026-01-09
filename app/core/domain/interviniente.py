from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import  relationship


class Interviniente(BaseModel):
    __tablename__ = "interviniente1"

    interviniente_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre = Column(String(200), nullable=False)
    direccion = Column(Text, nullable=True)
    ciudad = Column(String(200), nullable=True)
    pais_codigo = Column(String(40), nullable=True)
    telefono = Column(String(20), nullable=True)
    tipo_documento_codigo = Column(String(40), nullable=True)
    numero_documento = Column(String(20), nullable=True)
    tipo_codigo = Column(String(40), nullable=False)