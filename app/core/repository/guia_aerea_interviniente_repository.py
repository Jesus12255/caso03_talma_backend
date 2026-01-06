from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from app.integration.base_repository import BaseRepository


class GuiaAereaIntervinienteRepository(BaseRepository[GuiaAereaInterviniente]):
    
    async def get_by_guia_aerea_id(self, guia_aerea_id: str) -> list[GuiaAereaInterviniente]:
        pass