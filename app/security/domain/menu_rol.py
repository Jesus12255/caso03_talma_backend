from sqlalchemy import Column, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.domain.base_model import BaseModel

class MenuRol(BaseModel):
    __tablename__ = "menu_rol"

    menu_rol_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_maestro_id = Column(UUID(as_uuid=True), ForeignKey("menu_maestro.menu_maestro_id"))
    rol_id = Column(UUID(as_uuid=True), ForeignKey("rol.rol_id"))
    habilitado = Column(Boolean, default=True)

    menu = relationship("MenuMaestro", back_populates="menu_roles")
    rol = relationship("Rol")
