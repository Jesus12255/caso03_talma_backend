from uuid import UUID
from abc import abstractmethod
from dto.notificacion import NotificacionRequest
from abc import ABC

class NotificacionService(ABC):
    
    @abstractmethod
    async def save(self, request: NotificacionRequest):
        pass

    @abstractmethod
    async def get_user_notifications(self, user_id: str):
        pass

    @abstractmethod
    async def visto(self, notificacion_id: UUID):
        pass

    @abstractmethod
    async def resolver(self, guia_aerea_id: UUID):
        pass