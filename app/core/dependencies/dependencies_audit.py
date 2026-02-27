from app.configuration.dependencies.dependencies_catalogo import get_comun_facade
from app.core.repository.impl.audit_filtro_repository_impl import AuditFiltroRepositoryImpl
from app.core.facade.impl.audit_facade_impl import AuditFacadeImpl
from app.core.services.impl.audit_service_impl import AuditServiceImpl
from app.core.repository.impl.audit_repository_impl import AuditRepositoryImpl
from fastapi import Depends
from config.database_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession


def get_audit_repository(db: AsyncSession = Depends(get_db)):
    return AuditRepositoryImpl(db)

def get_audit_filtro_repository(db: AsyncSession = Depends(get_db)):
    return AuditFiltroRepositoryImpl(db)

def get_audit_service(repository = Depends(get_audit_repository), filtro_repository = Depends(get_audit_filtro_repository)):
    return AuditServiceImpl(repository, filtro_repository)

def get_audit_facade(service = Depends(get_audit_service), comun_facade = Depends(get_comun_facade)):
    return AuditFacadeImpl(service, comun_facade)
