from app.core.domain.notificacion import Notificacion
from app.core.repository.notificacion_repository import NotificacionRepository
from sqlalchemy.ext.asyncio import AsyncSession

class NotificacionRepositoryImpl(NotificacionRepository):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Notificacion, db)
