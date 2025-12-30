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
import re

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
            documento.estado_registro_codigo = Constantes.EstadoGuiaAerea.PROCESANDO
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
    
    async def get_with_relations(self, documentoId: str):
        documento = await self.document_repository.get_by_id_with_relations(documentoId)
        if documento is not None:
            return documento
        raise AppBaseException("El documento no se encuentra registrado")
    
    async def apply_business_rules(self, doc: GuiaAerea):
        await self._validar_confiabilidad(doc)
        await self._validar_duplicados(doc)
        await self._validar_numero_formato(doc)
        doc.modificado = DateUtil.get_current_local_datetime()
        doc.modificado_por = Constantes.SYSTEM_USER
        doc.estado_confianza = Constantes.EstadoConfianza.AUTO_VALIDADO
        if not doc.estado_registro_codigo or doc.estado_registro_codigo != Constantes.EstadoGuiaAerea.OBSERVADO:
            doc.estado_registro_codigo = Constantes.EstadoGuiaAerea.PROCESADO
        await self.document_repository.save(doc)


    async def _validar_confiabilidad(self, doc: GuiaAerea):
        if doc.numero and doc.confianzas_extraccion and len(doc.confianzas_extraccion) > 0:
            weighted_sum = 0.0
            total_weight_found = 0.0 
            def camel_to_snake_upper(name):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

            for conf in doc.confianzas_extraccion:
                field_key = camel_to_snake_upper(conf.nombre_campo.replace(".", "_"))
                weight = getattr(Constantes.PesoCampoGuiaAerea, field_key, 0.0) 
                
                if weight > 0:
                    weighted_sum += conf.confidence_modelo * weight
                    total_weight_found += weight
            
            doc.confidence_total = weighted_sum 

            if doc.confidence_total < 0.95:
                doc.estado_registro_codigo = Constantes.EstadoGuiaAerea.OBSERVADO
                obs = f" Nivel de confianza ponderado insuficiente ({doc.confidence_total:.2%}). Se requiere revisión manual. "
                doc.observaciones = (doc.observaciones or "") + obs + "\n"
    async def _validar_duplicados(self, doc: GuiaAerea):
        duplicado = await self.document_repository.find_by_numero(doc.numero, str(doc.guia_aerea_id))
        if duplicado:
            doc.estado_registro_codigo = Constantes.EstadoGuiaAerea.OBSERVADO
            obs = f" Número de guía duplicado. Ya existe en la guía con ID {duplicado.guia_aerea_id}. "
            doc.observaciones = (doc.observaciones or "") + obs + "\n"
    async def _validar_numero_formato(self, doc: GuiaAerea):
        pattern = r"^\d{3}-\d{8}$"
        if  doc.numero and re.match(pattern, doc.numero):
            doc.tipo_codigo = Constantes.TipoGuiaAerea.MAESTRA
        else:
            doc.estado_registro_codigo = Constantes.EstadoGuiaAerea.OBSERVADO
            obs = " Formato de número de guía inválido (No cumple formato MAWB: XXX-XXXXXXXX). "
            doc.observaciones = (doc.observaciones or "") + obs
