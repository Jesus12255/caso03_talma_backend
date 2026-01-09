from abc import ABC, abstractmethod

from uuid import UUID

from dto.interviniente_dtos import IntervinienteRequest


class IntervinienteService(ABC):
    
    @abstractmethod
    async def save(self, request: IntervinienteRequest) -> UUID:
        pass