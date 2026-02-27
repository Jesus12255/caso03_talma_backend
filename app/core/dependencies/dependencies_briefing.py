from fastapi import Depends
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.repository.impl.perfil_riesgo_repository_impl import PerfilRiesgoRepositoryImpl
from app.configuration.repository.impl.catalogo_repository_impl import CatalogoRepositoryImpl
from app.core.services.impl.briefing_service_impl import BriefingServiceImpl
from app.core.services.briefing_service import BriefingService
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_config import get_db

async def get_briefing_service(db: AsyncSession = Depends(get_db)) -> BriefingService:
    doc_repo = DocumentRepositoryImpl(db)
    risk_repo = PerfilRiesgoRepositoryImpl(db)
    cat_repo = CatalogoRepositoryImpl(db)
    return BriefingServiceImpl(doc_repo, risk_repo, cat_repo)
