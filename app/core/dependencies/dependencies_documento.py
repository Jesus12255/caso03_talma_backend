from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies.dependencies_confianza_extraccion import get_confianza_extraccion_service
from app.core.dependencies.dependencies_interviniente import get_interviniente_service
from app.core.facade.impl.document_facade_impl import DocumentFacadeImpl
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.services.impl.document_service_impl import DocumentServiceImpl
from config.database_config import get_db

def get_document_repository(db: AsyncSession = Depends(get_db)):
    return DocumentRepositoryImpl(db)

def get_document_service(repository = Depends(get_document_repository), interviniente_service = Depends(get_interviniente_service), confianza_extraccion_service = Depends(get_confianza_extraccion_service)):
    return DocumentServiceImpl(repository, interviniente_service, confianza_extraccion_service)

def get_document_facade(service = Depends(get_document_service)):
    return DocumentFacadeImpl(service)
