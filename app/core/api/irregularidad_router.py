from dto.perfil_riesgo_dtos import PerfilRiesgoComboResponse
from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest, PerfilRiesgoResponse, PerfilRiesgoDispersionResponse
from dto.collection_response import CollectionResponse
from dto.perfil_riesgo_dtos import PerfilRiesgoDataGridResponse
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

@router.get("/initFindPerfiles", response_model=PerfilRiesgoComboResponse)
async def initFindPerfiles(irregularidad_facade: IrregularidadFacade = Depends(get_irregularidad_facade)) -> PerfilRiesgoComboResponse:
    return await irregularidad_facade.initFindPerfiles()

@router.post("/findPerfiles", response_model=CollectionResponse[PerfilRiesgoDataGridResponse])
async def findPerfiles(request: PerfilRiesgoFiltroRequest, irregularidad_facade: IrregularidadFacade = Depends(get_irregularidad_facade)) -> CollectionResponse[PerfilRiesgoDataGridResponse]:
    return await irregularidad_facade.findPerfiles(request)

@router.get("/getPerfilById/{id}", response_model=PerfilRiesgoResponse)
async def getPerfilById(id: str, irregularidad_facade: IrregularidadFacade = Depends(get_irregularidad_facade)) -> PerfilRiesgoResponse:
    return await irregularidad_facade.getPerfilById(id)

@router.get("/perfiles/{id}/dispersion", response_model=PerfilRiesgoDispersionResponse)
async def getPerfilDispersion(id: str, irregularidad_facade: IrregularidadFacade = Depends(get_irregularidad_facade)) -> PerfilRiesgoDispersionResponse:
    return await irregularidad_facade.getPerfilDispersion(id)
