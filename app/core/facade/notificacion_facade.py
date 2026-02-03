
from abc import abstractmethod, ABC
from uuid import UUID

class NotificacionFacade(ABC):
    
    @abstractmethod
    def visto(self, notificacion_id: UUID):
        pass
