from app.core.facade.notificacion_facade import NotificacionFacade
from app.core.dependencies.dependencies_notificacion import get_notificacion_facade
from dto.universal_dto import BaseOperacionResponse
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from dto.notificacion import NotificacionResponse

router = APIRouter()

@router.get("/load", response_model=List[NotificacionResponse])
async def load(notificacion_facade: NotificacionFacade = Depends(get_notificacion_facade)):
    return await notificacion_facade.load()

@router.patch("/visto/{notificacion_id}", response_model=BaseOperacionResponse)
async def visto(notificacion_id: UUID, notificacion_facade: NotificacionFacade = Depends(get_notificacion_facade)):
    return await notificacion_facade.visto(notificacion_id)
    