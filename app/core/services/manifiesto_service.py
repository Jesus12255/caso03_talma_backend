from app.core.domain.guia_aerea import GuiaAerea
from abc import ABC, abstractmethod

class ManifiestoService(ABC):

    @abstractmethod
    async def associate_guia(self, guia_aerea: GuiaAerea):
        pass