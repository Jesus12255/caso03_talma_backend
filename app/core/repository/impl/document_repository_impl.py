from sqlalchemy.ext.asyncio import AsyncSession
from app.core.domain.guia_aerea import  GuiaAerea
from sqlalchemy import select

from app.core.repository.document_repository import DocumentRepository
from app.integration.impl.base_repository_impl import BaseRepositoryImpl



class DocumentRepositoryImpl(BaseRepositoryImpl[GuiaAerea], DocumentRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(GuiaAerea, db)

    