from abc import ABC, abstractmethod

from dto.guia_aerea_dtos import GuiaAereaRequest

class ConfianzaExtraccionService(ABC):

    @abstractmethod
    async def save(self, request: GuiaAereaRequest):
        pass