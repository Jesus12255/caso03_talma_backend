from sqlalchemy import select
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from app.core.repository.guia_aerea_interviniente_repository import GuiaAereaIntervinienteRepository
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession


class GuiaAereaIntervinienteRepositoryImpl(BaseRepositoryImpl[GuiaAereaInterviniente], GuiaAereaIntervinienteRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(GuiaAereaInterviniente, db)

    async def get_by_guia_aerea_id(self, guia_aerea_id: str) -> list[GuiaAereaInterviniente]:
        query = select(GuiaAereaInterviniente).where(
            GuiaAereaInterviniente.guia_aerea_id == guia_aerea_id,
            GuiaAereaInterviniente.es_version_activa == True,
            GuiaAereaInterviniente.habilitado == True
        ).order_by(GuiaAereaInterviniente.version.desc())
        result = await self.db.execute(query)
        return result.scalars().all()