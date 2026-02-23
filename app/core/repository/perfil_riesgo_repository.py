from abc import abstractmethod
from app.integration.base_repository import BaseRepository
from app.core.domain.perfil_riesgo import PerfilRiesgo
from typing import Optional, List

class PerfilRiesgoRepository(BaseRepository[PerfilRiesgo]):

    @abstractmethod
    async def find_by_vector_similarity(self, embedding: List[float], tipo: str, threshold: float = 0.2) -> Optional[PerfilRiesgo]:
        pass

    @abstractmethod
    async def find_dispersion_by_perfil(self, perfil_riesgo_id: str) -> dict:
        pass
