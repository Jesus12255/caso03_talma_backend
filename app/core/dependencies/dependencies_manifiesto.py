
from app.core.services.impl.manifiesto_service_impl import ManifiestoServiceImpl
from app.core.repository.impl.manifiesto_repository_impl import ManifiestoRepositoryImpl
from fastapi import Depends
from config.database_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession


def get_manifiesto_repository(db: AsyncSession = Depends(get_db)):
    return ManifiestoRepositoryImpl(db)

def get_manifiesto_service(repository = Depends(get_manifiesto_repository), db: AsyncSession = Depends(get_db)):
    from core.service.service_container import ServiceContainer
    container = ServiceContainer(db)
    return container.manifiesto_service