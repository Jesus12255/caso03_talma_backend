
from app.core.repository.impl.perfil_riesgo_filtro_repository_impl import PerfilRiesgoFiltroRepositoryImpl
from app.core.services.impl.perfil_riesgo_service_impl import PerfilRiesgoServiceImpl
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from config.database_config import get_db

from app.core.repository.impl.perfil_riesgo_repository_impl import PerfilRiesgoRepositoryImpl

def get_perfil_riesgo_filtro_repository(db: AsyncSession = Depends(get_db)):
    return PerfilRiesgoFiltroRepositoryImpl(db)

def get_perfil_riesgo_repository(db: AsyncSession = Depends(get_db)):
    return PerfilRiesgoRepositoryImpl(db)

def get_perfil_riesgo_service(repository = Depends(get_perfil_riesgo_filtro_repository), perfil_repo = Depends(get_perfil_riesgo_repository)):
    return PerfilRiesgoServiceImpl(repository, perfil_repo)
