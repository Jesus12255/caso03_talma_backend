from app.core.services.impl.notificacion_service_impl import NotificacionServiceImpl
from app.core.repository.impl.notificacion_repository_impl import NotificacionRepositoryImpl
from fastapi import Depends
from config.database_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession


def get_notificacion_repository(db: AsyncSession = Depends(get_db)):
    return NotificacionRepositoryImpl(db)

def get_notificacion_service(repository = Depends(get_notificacion_repository)):
    return NotificacionServiceImpl(repository)
