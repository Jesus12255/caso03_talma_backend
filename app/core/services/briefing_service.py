from abc import ABC, abstractmethod

class BriefingService(ABC):
    @abstractmethod
    async def get_operational_summary(self) -> dict:
        """Obtiene un resumen de la operación actual."""
        pass

    @abstractmethod
    async def get_observed_guides_details(self) -> list[dict]:
        """Obtiene el listado detallado de guías observadas y sus motivos."""
        pass

    @abstractmethod
    async def get_catalogo_entry(self, codigo: str) -> dict:
        """Obtiene la descripción y detalles de un código del catálogo."""
        pass

    @abstractmethod
    async def search_catalogo_by_reference(self, referencia_codigo: str) -> list[dict]:
        """Obtiene todos los elementos de una categoría del catálogo."""
        pass
