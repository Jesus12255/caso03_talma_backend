from dto.universal_dto import BaseOperacionResponse
from uuid import UUID
from abc import abstractmethod, ABC

class IrregularidadFacade(ABC):
   
    @abstractmethod
    async def validarExcepcion(self, notificacion_id: UUID) -> BaseOperacionResponse:
        pass