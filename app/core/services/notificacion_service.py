from abc import abstractmethod
from dto.notificacion import NotificacionRequest
from abc import ABC

class NotificacionService(ABC):
    
    @abstractmethod
    async def save(self, request: NotificacionRequest):
        pass