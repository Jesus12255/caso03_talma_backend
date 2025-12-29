from abc import abstractmethod

from uuid import UUID
from app.core.domain.interviniente import Interviniente
from app.core.repository.interviniente_repository import IntervinienteRepository
from app.core.services.interviniente_service import IntervinienteService
from config.mapper import Mapper
from core.service.service_base import ServiceBase
from dto.interviniente_dtos import IntervinienteRequest


class IntervinienteServiceImpl(IntervinienteService, ServiceBase):

    def __init__(self, interviniente_repository: IntervinienteRepository):
        self.interviniente_repository = interviniente_repository
    
    async def save(self, request: IntervinienteRequest) -> UUID:
        interviniente = Mapper.to_entity(request, Interviniente)
        await self.interviniente_repository.save(interviniente)
        return interviniente.interviniente_id