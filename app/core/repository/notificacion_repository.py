from abc import abstractmethod
from uuid import UUID
from app.core.domain.notificacion import Notificacion
from app.integration.impl.base_repository_impl import BaseRepositoryImpl

class NotificacionRepository(BaseRepositoryImpl[Notificacion]):
    async def find_by_user_id(self, user_id: str):
        raise NotImplementedError

    @abstractmethod
    async def find_by_guia_aerea_id(self, guia_aerea_id: UUID) -> list[Notificacion]:
        raise NotImplementedError

    