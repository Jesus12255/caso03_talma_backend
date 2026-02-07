from abc import ABC, abstractmethod
from typing import List
from app.security.domain.menu_maestro import MenuMaestro

class MenuRepository(ABC):
    
    @abstractmethod
    async def find_all_enabled(self) -> List[MenuMaestro]:
        pass

    @abstractmethod
    async def find_by_rol_id(self, rol_id: str) -> List[MenuMaestro]:
        pass
