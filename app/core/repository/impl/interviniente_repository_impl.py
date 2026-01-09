from app.core.domain.interviniente import Interviniente
from app.core.repository.interviniente_repository import IntervinienteRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class IntervinienteRepositoryImpl(IntervinienteRepository):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Interviniente, db)

    async def find_by_documento_tipo(self, numero_documento: str, tipo_codigo: str) -> Interviniente | None:
        query = select(Interviniente).where(
            Interviniente.numero_documento == numero_documento,
            Interviniente.tipo_codigo == tipo_codigo
        )
        result = await self.db.execute(query)
        return result.scalars().first()