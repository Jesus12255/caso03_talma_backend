from app.core.domain.guia_aerea import  GuiaAerea
from app.core.repository.document_repository import DocumentRepository
from app.core.services.confianza_extraccion_service import ConfianzaExtraccionService
from app.core.services.document_service import DocumentService
from app.core.services.interviniente_service import IntervinienteService
from config.mapper import Mapper
from core.exceptions import AppBaseException
from core.service.service_base import ServiceBase
from dto.guia_aerea_dtos import  GuiaAereaRequest
from utl.constantes import Constantes
from utl.date_util import DateUtil


class DocumentServiceImpl(DocumentService, ServiceBase):

    def __init__(self, document_repository: DocumentRepository, interviniente_service: IntervinienteService, confianza_extraccion_service: ConfianzaExtraccionService):
        self.document_repository = document_repository
        self.interviniente_service = interviniente_service
        self.confianza_extraccion_service = confianza_extraccion_service

    async def saveOrUpdate(self, t: GuiaAereaRequest):
        if t.guiaAereaId:
            documento = await self.get(t.guiaAereaId)
            documento.nombre = t.nombre
            documento.confiabilidad = t.confiabilidad
            documento.anonimizado = t.anonimizado   
            documento.datos = [dato.model_dump() for dato in t.datos]
            documento.modificado = DateUtil.get_current_local_datetime()
            documento.modificado_por = self.session.full_name
            await self.document_repository.save(documento)
        else: 
            documento = Mapper.to_entity(t, GuiaAerea)
            documento.habilitado = Constantes.HABILITADO
            documento.creado = DateUtil.get_current_local_datetime()
            documento.creado_por = self.session.full_name
            documento.remitente_id = await self.interviniente_service.save(t.intervinientes[0])
            documento.consignatario_id = await self.interviniente_service.save(t.intervinientes[1])
            await self.document_repository.save(documento)
            t.guiaAereaId = documento.guia_aerea_id
            t.intervinientes[0].intervinienteId = documento.remitente_id
            t.intervinientes[1].intervinienteId = documento.consignatario_id
            await self.confianza_extraccion_service.save(t)

    async def get_all_documents(self, skip: int = 0, limit: int = 10):
        return await self.document_repository.find_all(skip, limit)


    async def get(self, documentoId: str):
        documento = await self.document_repository.get_by_id(documentoId)
        if documento is not None:
            return documento
        raise AppBaseException("El documento no se encuentra registrado")
