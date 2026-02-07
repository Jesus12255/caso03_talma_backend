from typing import List, Optional
from pydantic import BaseModel

class MenuDto(BaseModel):
    menuId: str
    nombre: str
    descripcion: str
    url: Optional[str] = None
    icono: Optional[str] = None
    orden: int
    referenciaId: Optional[str] = None
    submenus: List['MenuDto'] = []
    habilitado: bool

class MenuResponse(BaseModel):
    menus: List[MenuDto]
