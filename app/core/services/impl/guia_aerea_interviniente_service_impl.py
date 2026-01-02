from typing import List, Optional

from app.core.domain.confianza_extraccion import ConfianzaExtraccion
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from app.core.repository.confianza_extraccion_repository import ConfianzaExtraccionRepository
from app.core.repository.guia_aerea_interviniente_repository import GuiaAereaIntervinienteRepository
from app.core.services.guia_aerea_interviniente_service import GuiaAereaIntervinienteService
from config.mapper import Mapper
from core.exceptions import AppBaseException
from core.service.service_base import ServiceBase
from dto.guia_aerea_dtos import GuiaAereaRequest
from dto.confianza_extraccion_dtos import GuiaAereaConfianzaRequest
from dto.interviniente_dtos import IntervinienteRequest
from utl.constantes import Constantes
from utl.date_util import DateUtil


class GuiaAereaIntervinienteServiceImpl( GuiaAereaIntervinienteService, ServiceBase):

    def __init__(self, guia_aerea_interviniente_repository: GuiaAereaIntervinienteRepository, confianza_extraccion_repository: ConfianzaExtraccionRepository):
        self.guia_aerea_interviniente_repository = guia_aerea_interviniente_repository
        self.confianza_extraccion_repository = confianza_extraccion_repository

    async def save(self, request: GuiaAereaRequest):

        remitente_req = self._find_interviniente(request.intervinientes, Constantes.TipoInterviniente.REMITENTE)
        consignatario_req = self._find_interviniente(request.intervinientes, Constantes.TipoInterviniente.CONSIGNATARIO)

        await self._save_interviniente(remitente_req, "remitente", request.confianzas, Constantes.TipoInterviniente.REMITENTE, request.guiaAereaId)
        await self._save_interviniente(consignatario_req, "consignatario", request.confianzas, Constantes.TipoInterviniente.CONSIGNATARIO, request.guiaAereaId)

    async def get_by_guia_aerea_id(self, guia_aerea_id: str) -> List[GuiaAereaInterviniente]:
        return await self.guia_aerea_interviniente_repository.get_by_guia_aerea_id(guia_aerea_id)

    async def get_by_id(self, id: str) -> GuiaAereaInterviniente:
        return await self.guia_aerea_interviniente_repository.get_by_id(id)

    async def update(self, interviniente: GuiaAereaInterviniente) -> GuiaAereaInterviniente:
        return await self.guia_aerea_interviniente_repository.save(interviniente)




    async def _save_interviniente(self, request: IntervinienteRequest, rol_codigo: str, confianzas: Optional[List[GuiaAereaConfianzaRequest]], tipo: str, guia_aerea_id: str):
        guia_aerea_interviniente = Mapper.to_entity(request, GuiaAereaInterviniente)
        prefijo = rol_codigo.lower()
        guia_aerea_interviniente.guia_aerea_id = guia_aerea_id
        guia_aerea_interviniente.rol_codigo = tipo
        guia_aerea_interviniente.version = 1
        guia_aerea_interviniente.habilitado = Constantes.HABILITADO
        guia_aerea_interviniente.creado = DateUtil.get_current_local_datetime()
        guia_aerea_interviniente.creado_por = Constantes.SYSTEM_USER
        await self.guia_aerea_interviniente_repository.save(guia_aerea_interviniente)
        
        confianzas_extraccion = []
        confianzas_extraccion.append(self._save_confianza_extraccion(guia_aerea_interviniente, tipo, confianzas, f"{prefijo}.nombre"))
        confianzas_extraccion.append(self._save_confianza_extraccion(guia_aerea_interviniente, tipo, confianzas, f"{prefijo}.direccion"))
        confianzas_extraccion.append(self._save_confianza_extraccion(guia_aerea_interviniente, tipo, confianzas, f"{prefijo}.ciudad"))
        confianzas_extraccion.append(self._save_confianza_extraccion(guia_aerea_interviniente, tipo, confianzas, f"{prefijo}.paisCodigo"))
        confianzas_extraccion.append(self._save_confianza_extraccion(guia_aerea_interviniente, tipo, confianzas, f"{prefijo}.numeroDocumento"))
        confianzas_extraccion.append(self._save_confianza_extraccion(guia_aerea_interviniente, tipo, confianzas, f"{prefijo}.telefono"))
        await self.confianza_extraccion_repository.save_all(confianzas_extraccion)

    def _find_interviniente(self, intervinientes: List[IntervinienteRequest], rol_codigo: str ) -> IntervinienteRequest:
        for inter in intervinientes:
            if inter.tipoCodigo == rol_codigo:
                return inter

        raise AppBaseException(
            f"No se encontró interviniente con tipoCodigo={rol_codigo}"
        )

    def _save_confianza_extraccion(self, guia_aerea_interviniente: GuiaAereaInterviniente,  tipo: str, confianzas: Optional[List[GuiaAereaConfianzaRequest]], campo: str) -> ConfianzaExtraccion:
        confianzaRequest = self._get_confidence( campo, confianzas)
        confianza_extraccion = ConfianzaExtraccion()
        confianza_extraccion.entidad_tipo = tipo
        confianza_extraccion.entidad_id = guia_aerea_interviniente.guia_aerea_interviniente_id
        confianza_extraccion.nombre_campo = campo
        confianza_extraccion.valor_extraido = guia_aerea_interviniente.nombre
        confianza_extraccion.confidence_modelo = confianzaRequest.confidenceModelo
        confianza_extraccion.habilitado = Constantes.HABILITADO
        confianza_extraccion.creado = DateUtil.get_current_local_datetime()
        confianza_extraccion.creado_por = Constantes.SYSTEM_USER
        confianzaRequest.intervinienteId = guia_aerea_interviniente.guia_aerea_interviniente_id
        return confianza_extraccion

    def _get_confidence( self, field_name: str, confianzas: Optional[List[GuiaAereaConfianzaRequest]]) -> GuiaAereaConfianzaRequest:
        target = field_name.lower().strip()

        for c in confianzas:
            if c.nombreCampo.lower().strip() == target:
                return c

