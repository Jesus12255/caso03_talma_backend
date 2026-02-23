
from app.core.domain.perfil_riesgo_data_grid import PerfilRiesgoDataGrid
from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest
from app.core.repository.perfil_riesgo_filtro_repository import PerfilRiesgoFiltroRepository
from core.service.service_base import ServiceBase
from app.core.services.perfil_riesgo_service import PerfilRiesgoService

from app.core.repository.perfil_riesgo_repository import PerfilRiesgoRepository
from app.core.domain.perfil_riesgo import PerfilRiesgo

class PerfilRiesgoServiceImpl(PerfilRiesgoService, ServiceBase):

    def __init__(self, perfil_riesgo_filtro_repository: PerfilRiesgoFiltroRepository, perfil_riesgo_repository: PerfilRiesgoRepository):
        self.perfil_riesgo_filtro_repository = perfil_riesgo_filtro_repository
        self.perfil_riesgo_repository = perfil_riesgo_repository

    
    async def find(self, request: PerfilRiesgoFiltroRequest) -> tuple[list[PerfilRiesgoDataGrid], int]:
        filters = []

        if request.tipoIntervinienteCodigo:
            filters.append(PerfilRiesgoDataGrid.tipo_interviniente_codigo == request.tipoIntervinienteCodigo)
        if request.nombreNormalizado:
            filters.append(PerfilRiesgoDataGrid.nombre_normalizado.ilike(f"%{request.nombreNormalizado.upper()}%"))
        if request.fechaInicio:
            filters.append(PerfilRiesgoDataGrid.creado >= request.fechaInicio)
        if request.fechaFin:
            filters.append(PerfilRiesgoDataGrid.creado <= request.fechaFin)
        if request.cantidadEnviosMaximo:
            filters.append(PerfilRiesgoDataGrid.cantidad_envios <= request.cantidadEnviosMaximo)
        if request.cantidadEnviosMinimo:
            filters.append(PerfilRiesgoDataGrid.cantidad_envios >= request.cantidadEnviosMinimo)

        data, total_count = await self.perfil_riesgo_filtro_repository.find_data_grid(
            filters=filters,
            start=request.start,
            limit=request.limit,
            sort=request.sort
        )
        return data, total_count

    async def getPerfilById(self, id: str) -> PerfilRiesgo:
        return await self.perfil_riesgo_repository.get_by_id(id)

    async def get_dispersion(self, id: str) -> dict:
        return await self.perfil_riesgo_repository.find_dispersion_by_perfil(id)