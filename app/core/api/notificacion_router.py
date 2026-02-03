from app.core.facade.notificacion_facade import NotificacionFacade
from app.core.dependencies.dependencies_notificacion import get_notificacion_facade
from dto.universal_dto import BaseOperacionResponse
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from app.core.services.notificacion_service import NotificacionService
from app.core.dependencies.dependencies_notificacion import get_notificacion_service
from app.auth.dependencies.dependencies_auth import get_current_user
from core.context.user_context import get_user_session
from dto.notificacion import NotificacionResponse

router = APIRouter()

@router.get("/", response_model=List[NotificacionResponse])
async def get_my_notifications(
    service: NotificacionService = Depends(get_notificacion_service),
    username: str = Depends(get_current_user)
):
    session = get_user_session()
    entities = await service.get_user_notifications(str(session.user_id))
    
    dtos = []
    for e in entities:
        dtos.append(NotificacionResponse(
            notificacionId=e.notificacion_id,
            guiaAereaId=e.guia_aerea_id,
            usuarioId=e.usuario_id,
            tipoCodigo=e.tipo_codigo,
            titulo=e.titulo,
            mensaje=e.mensaje,
            severidadCodigo=e.severidad_codigo,
            estadoCodigo=e.estado_codigo,
            creado=e.creado.isoformat() if e.creado else ""
        ))
    return dtos

@router.patch("/visto/{notificacion_id}", response_model=BaseOperacionResponse)
async def visto(notificacion_id: UUID, notificacion_facade: NotificacionFacade = Depends(get_notificacion_facade)):
    return await notificacion_facade.visto(notificacion_id)
    