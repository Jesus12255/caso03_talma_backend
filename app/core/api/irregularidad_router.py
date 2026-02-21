from uuid import UUID
from app.core.dependencies.dependencies_irregularidad import get_irregularidad_facade
from fastapi import Depends
from app.core.facade.irregularidad_facade import IrregularidadFacade
from dto.universal_dto import BaseOperacionResponse
from fastapi import APIRouter

router = APIRouter()

@router.post("/validarExcepcion/{notificacion_id}", response_model=BaseOperacionResponse)
async def validarExcepcion(notificacion_id: UUID, irregularidad_facade: IrregularidadFacade = Depends(get_irregularidad_facade)) -> BaseOperacionResponse:
    return await irregularidad_facade.validarExcepcion(notificacion_id)