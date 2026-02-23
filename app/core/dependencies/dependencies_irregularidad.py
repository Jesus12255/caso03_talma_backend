
from app.configuration.dependencies.dependencies_catalogo import get_comun_facade
from app.core.dependencies.dependencies_perfil_riesgo import get_perfil_riesgo_service
from app.core.dependencies.dependencies_audit import get_audit_service
from app.integration.dependencies.dependencies_embedding import get_embedding_service
from app.core.dependencies.dependencies_guia_aerea_interviniente import get_guia_aerea_interviniente_service
from app.core.dependencies.dependencies_repositories import get_document_repository
from app.core.dependencies.dependencies_notificacion import get_notificacion_repository, get_notificacion_service
from app.core.facade.impl.irregularidad_facade_impl import IrregularidadFacadeImpl
from app.core.services.impl.irregularidad_service_impl import IrregularidadServiceImpl
from app.core.repository.impl.perfil_riesgo_repository_impl import PerfilRiesgoRepositoryImpl
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_config import get_db

def get_perfil_riesgo_repository(db: AsyncSession = Depends(get_db)):
    return PerfilRiesgoRepositoryImpl(db)

def get_irregularidad_service(
    perfil_repo = Depends(get_perfil_riesgo_repository), 
    notificacion_repo = Depends(get_notificacion_repository), 
    notificacion_service = Depends(get_notificacion_service),
    document_repo = Depends(get_document_repository), 
    guia_aerea_interviniente_service = Depends(get_guia_aerea_interviniente_service), 
    embedding_service = Depends(get_embedding_service), 
    auditoria_service = Depends(get_audit_service)
    ):
    return IrregularidadServiceImpl(perfil_repo, notificacion_repo, notificacion_service, document_repo, guia_aerea_interviniente_service, embedding_service, auditoria_service)

def get_irregularidad_facade(service = Depends(get_irregularidad_service), perfil_riesgo_service = Depends(get_perfil_riesgo_service), comun_facade = Depends(get_comun_facade)):
    return IrregularidadFacadeImpl(service, perfil_riesgo_service, comun_facade)
