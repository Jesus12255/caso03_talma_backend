from dto.universal_dto import BaseOperacionResponse
from uuid import UUID
from app.core.services.IrregularidadService import IrregularidadService
from app.core.facade.irregularidad_facade import IrregularidadFacade
from core.facade.facade_base import FacadeBase

class IrregularidadFacadeImpl(IrregularidadFacade, FacadeBase):

    def __init__(self, irregularidad_service: IrregularidadService):
        self.irregularidad_service = irregularidad_service

    async def validarExcepcion(self, notificacion_id: UUID) -> BaseOperacionResponse:
        await self.irregularidad_service.validarExcepcion(notificacion_id)
        return BaseOperacionResponse(codigo="200", mensaje="Excepción validada correctamente.")