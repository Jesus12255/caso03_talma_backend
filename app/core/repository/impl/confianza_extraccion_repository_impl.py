from app.core.domain.confianza_extraccion import ConfianzaExtraccion
from app.core.repository.confianza_extraccion_repository import ConfianzaExtraccionRepository
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession

class ConfianzaExtraccionRepositoryImpl(BaseRepositoryImpl[ConfianzaExtraccion], ConfianzaExtraccionRepository):
    
    def __init__(self, db: AsyncSession):
        super().__init__(ConfianzaExtraccion, db)

    
    