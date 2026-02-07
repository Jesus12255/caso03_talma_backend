from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.domain.base_model import BaseModel

class MenuMaestro(BaseModel):
    __tablename__ = "menu_maestro"

    menu_maestro_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100))
    descripcion = Column(String(200))
    url = Column(String(500))
    icono = Column(String(100))
    orden = Column(Integer)
    referencia_id = Column(UUID(as_uuid=True), ForeignKey("menu_maestro.menu_maestro_id"), nullable=True)
    habilitado = Column(Boolean, default=True)

    submenus = relationship("MenuMaestro", remote_side=[menu_maestro_id], backref="padre")
    menu_roles = relationship("MenuRol", back_populates="menu")
    opciones = relationship("MenuOpcion", back_populates="menu")
