
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_config import get_db
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl


def get_document_repository(db: AsyncSession = Depends(get_db)):
    return DocumentRepositoryImpl(db)
