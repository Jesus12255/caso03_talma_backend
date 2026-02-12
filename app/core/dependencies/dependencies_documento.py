
from app.core.dependencies.dependencies_notificacion import get_notificacion_service
from app.core.dependencies.dependencies_audit import get_audit_service
from app.core.repository.impl.manifiesto_repository_impl import ManifiestoRepositoryImpl
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies.dependencies_confianza_extraccion import get_confianza_extraccion_repository, get_confianza_extraccion_service
from app.core.dependencies.dependencies_guia_aerea_interviniente import get_guia_aerea_interviniente_service
from app.core.dependencies.dependencies_interviniente import get_interviniente_service
from app.core.facade.impl.document_facade_impl import DocumentFacadeImpl
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.repository.impl.guia_aerea_filtro_repository_impl import GuiaAereaFiltroRepositoryImpl
from app.core.services.impl.document_service_impl import DocumentServiceImpl
from app.integration.service.impl.gcp_storage_service_impl import GcpStorageServiceImpl
from app.integration.service.storage_service import StorageService
from app.core.services.document_service import DocumentService
from config.database_config import get_db

def get_document_repository(db: AsyncSession = Depends(get_db)):
    return DocumentRepositoryImpl(db)

def get_guia_aerea_filtro_repository(db: AsyncSession = Depends(get_db)):
    return GuiaAereaFiltroRepositoryImpl(db)

def get_manifiesto_repository(db: AsyncSession = Depends(get_db)):
    return ManifiestoRepositoryImpl(db)

def get_storage_service() -> StorageService:
    return GcpStorageServiceImpl()

def get_document_service(
    repository = Depends(get_document_repository), 
    guia_aerea_filtro_repository = Depends(get_guia_aerea_filtro_repository), 
    interviniente_service = Depends(get_interviniente_service), 
    confianza_extraccion_service = Depends(get_confianza_extraccion_service), 
    confianza_extraccion_repository = Depends(get_confianza_extraccion_repository), 
    guia_aerea_interviniente_service = Depends(get_guia_aerea_interviniente_service),
    notificacion_service = Depends(get_notificacion_service),
    manifiesto_repository = Depends(get_manifiesto_repository),
    audit_service = Depends(get_audit_service)):
    return DocumentServiceImpl(repository,
    guia_aerea_filtro_repository,
    interviniente_service,
    confianza_extraccion_service,
    confianza_extraccion_repository,
    guia_aerea_interviniente_service,
    notificacion_service,
    manifiesto_repository,
    audit_service
    )

def get_document_facade(service: DocumentService = Depends(get_document_service), guia_aerea_interviniente_service = Depends(get_guia_aerea_interviniente_service), storage_service = Depends(get_storage_service)):
    return DocumentFacadeImpl(service, guia_aerea_interviniente_service, storage_service)
