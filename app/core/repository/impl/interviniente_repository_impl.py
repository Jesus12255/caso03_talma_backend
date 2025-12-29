from app.core.domain.interviniente import Interviniente
from app.core.repository.interviniente_repository import IntervinienteRepository
from sqlalchemy.ext.asyncio import AsyncSession

class IntervinienteRepositoryImpl(IntervinienteRepository):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Interviniente, db)