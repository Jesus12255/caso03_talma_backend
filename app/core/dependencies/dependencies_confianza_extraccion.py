from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.repository.impl.confianza_extraccion_repository_impl import ConfianzaExtraccionRepositoryImpl
from app.core.services.impl.confianza_extraccion_service_impl import ConfianzaExtraccionServiceImpl
from config.database_config import get_db

def get_confianza_extraccion_repository(db: AsyncSession = Depends(get_db)):
    return ConfianzaExtraccionRepositoryImpl(db)


def get_confianza_extraccion_service(repository = Depends(get_confianza_extraccion_repository)):
    return ConfianzaExtraccionServiceImpl(repository)