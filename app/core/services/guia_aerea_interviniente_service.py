from typing import List
from abc import ABC, abstractmethod
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from dto.guia_aerea_dtos import GuiaAereaRequest


class GuiaAereaIntervinienteService(ABC):
    
    @abstractmethod
    async def save(self, request: GuiaAereaRequest):
        pass

    @abstractmethod
    async def get_by_guia_aerea_id(self, guia_aerea_id: str) -> List[GuiaAereaInterviniente]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> GuiaAereaInterviniente:
        pass

    @abstractmethod
    async def update(self, interviniente: GuiaAereaInterviniente) -> GuiaAereaInterviniente:
        pass