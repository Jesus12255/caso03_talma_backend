from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.dependencies.dependencies_confianza_extraccion import get_confianza_extraccion_repository
from app.core.services.impl.guia_aerea_interviniente_service_impl import GuiaAereaIntervinienteServiceImpl
from config.database_config import get_db
from app.core.repository.impl.guia_aerea_interviniente_repository_impl import GuiaAereaIntervinienteRepositoryImpl

def get_guia_aerea_interviniente_repository(db: AsyncSession = Depends(get_db)):
    return GuiaAereaIntervinienteRepositoryImpl(db)

def get_guia_aerea_interviniente_service(repository = Depends(get_guia_aerea_interviniente_repository), confianza_extraccion_repository = Depends(get_confianza_extraccion_repository)):
    return GuiaAereaIntervinienteServiceImpl(repository, confianza_extraccion_repository)
