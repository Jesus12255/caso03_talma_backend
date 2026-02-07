from fastapi import APIRouter, Depends
from app.security.dependencies.dependencies_usuario import get_usuario_facade
from app.security.facade.usuario_facade import UsuarioFacade
from dto.collection_response import CollectionResponse
from dto.universal_dto import BaseOperacionResponse
from dto.usuario_dtos import UsuarioCambioPasswordRequest, UsuarioComboResponse, UsuarioFiltroRequest, UsuarioRequest, UsuarioResponse, UsuarioFiltroResponse, UsuarioStatusRequest
from dto.menu_dtos import MenuResponse


router = APIRouter()

@router.post("/saveOrUpdate", response_model=BaseOperacionResponse)
async def saveOrUpdate( request: UsuarioRequest, usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> BaseOperacionResponse:
    return await usuario_facade.saveOrUpdate(request)


@router.get("/init", response_model=UsuarioComboResponse)
async def init( usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> UsuarioComboResponse:
    return await usuario_facade.init()

@router.get("/initForm", response_model=UsuarioComboResponse)
async def initForm( usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> UsuarioComboResponse:
    return await usuario_facade.initForm()


@router.get("/loadMenu", response_model=MenuResponse)
async def loadMenu(usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> MenuResponse:
    return await usuario_facade.loadMenu()


@router.get("/{usuarioId}", response_model=UsuarioResponse)
async def get_usuario(usuarioId: str, usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> UsuarioResponse:
    return await usuario_facade.get(usuarioId)


@router.post("/find", response_model=CollectionResponse[UsuarioFiltroResponse])
async def find(request: UsuarioFiltroRequest, usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> CollectionResponse[UsuarioFiltroResponse]:
    return await usuario_facade.find(request)


@router.post("/changeStatus", response_model=BaseOperacionResponse)
async def changeStatus(request: UsuarioStatusRequest, usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> BaseOperacionResponse:
    return await usuario_facade.changeStatus(request)


@router.post("/updatePassword", response_model=BaseOperacionResponse)
async def updatePassword(request: UsuarioCambioPasswordRequest, usuario_facade: UsuarioFacade = Depends(get_usuario_facade)) -> BaseOperacionResponse:
    return await usuario_facade.updatePassword(request)

