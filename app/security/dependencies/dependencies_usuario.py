from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.configuration.dependencies.dependencies_catalogo import get_comun_facade

from app.security.facade.impl.usuario_facade_impl import UsuarioFacadeImpl
from app.security.repository.impl.usuario_repository_impl import UsuarioRepositoryImpl
from app.security.service.impl.usuario_service_impl import UsuarioServiceImpl
from config.database_config import get_db
from config.dependiencies.dependencies_config import get_model_mapper

from app.core.services.impl.email_service_impl import EmailServiceImpl

def get_email_service():
    return EmailServiceImpl()

def get_usuario_repository(db: AsyncSession = Depends(get_db)):
    return UsuarioRepositoryImpl(db)

def get_usuario_service(repository = Depends(get_usuario_repository), modelMapper = get_model_mapper(), email_service = Depends(get_email_service)):
    return UsuarioServiceImpl(repository, modelMapper, email_service)

def get_usuario_facade(service = Depends(get_usuario_service), modelMapper = get_model_mapper(), facade = Depends(get_comun_facade)):
    return UsuarioFacadeImpl(service, modelMapper, facade)
