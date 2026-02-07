from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.domain.base_model import BaseModel

class MenuOpcion(BaseModel):
    __tablename__ = "menu_opcion"

    menu_opcion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_maestro_id = Column(UUID(as_uuid=True), ForeignKey("menu_maestro.menu_maestro_id"))
    codigo = Column(String(100))
    nombre = Column(String(250))
    descripcion = Column(String(250))
    habilitado = Column(Boolean, default=True)

    menu = relationship("MenuMaestro", back_populates="opciones")
