
from typing import List, Any
from app.core.domain.guia_aerea import  GuiaAerea
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from app.core.repository.document_repository import DocumentRepository
from app.core.repository.guia_aerea_filtro_repository import GuiaAereaFiltroRepository
from app.core.services.confianza_extraccion_service import ConfianzaExtraccionService
from app.core.services.document_service import DocumentService
from app.core.services.interviniente_service import IntervinienteService
from config.mapper import Mapper
from core.exceptions import AppBaseException
from core.service.service_base import ServiceBase
from dto.guia_aerea_dtos import  GuiaAereaFiltroRequest, GuiaAereaRequest
from utl.constantes import Constantes
from utl.date_util import DateUtil
import re
from sqlalchemy import or_, and_

class DocumentServiceImpl(DocumentService, ServiceBase):

    def __init__(self, document_repository: DocumentRepository, guia_aerea_filtro_repository:GuiaAereaFiltroRepository , interviniente_service: IntervinienteService, confianza_extraccion_service: ConfianzaExtraccionService):
        self.document_repository = document_repository
        self.guia_aerea_filtro_repository = guia_aerea_filtro_repository
        self.interviniente_service = interviniente_service
        self.confianza_extraccion_service = confianza_extraccion_service

    async def saveOrUpdate(self, t: GuiaAereaRequest):
        if t.guiaAereaId:
            documento = await self.get(t.guiaAereaId)
            documento.numero = t.numero
            documento.tipo_codigo = t.tipoCodigo
            documento.fecha_emision = t.fechaEmision
            documento.origen_codigo = t.origenCodigo
            documento.destino_codigo = t.destinoCodigo
            documento.transbordo = t.transbordo
            documento.aerolinea_codigo = t.aerolineaCodigo
            documento.numero_vuelo = t.numeroVuelo
            documento.fecha_vuelo = t.fechaVuelo
            documento.descripcion_mercancia = t.descripcionMercancia
            documento.cantidad_piezas = t.cantidadPiezas
            documento.peso_bruto = t.pesoBruto
            documento.peso_cobrado = t.pesoCobrado
            documento.unidad_peso_codigo = t.unidadPesoCodigo
            documento.volumen = t.volumen
            documento.naturaleza_carga_codigo = t.naturalezaCargaCodigo
            documento.valor_declarado = t.valorDeclarado
            documento.tipo_flete_codigo = t.tipoFleteCodigo
            documento.tarifa_flete = t.tarifaFlete
            documento.otros_cargos = t.otrosCargos
            documento.moneda_codigo = t.monedaCodigo
            documento.total_flete = t.totalFlete
            documento.instrucciones_especiales = t.instruccionesEspeciales
            documento.observaciones = t.observaciones
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
            documento.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.PROCESANDO
            await self.document_repository.save(documento)
            t.guiaAereaId = documento.guia_aerea_id
            t.intervinientes[0].intervinienteId = documento.remitente_id
            t.intervinientes[1].intervinienteId = documento.consignatario_id
            await self.confianza_extraccion_service.save(t)

    async def find(self, request: GuiaAereaFiltroRequest) -> tuple[List[GuiaAereaDataGrid], int]:
        filters = []
        if  Constantes.Vista.GUIA_AEREA_REGISTROS ==  request.vistaCodigo:
            filters.append(and_(GuiaAereaDataGrid.estado_registro_codigo != Constantes.EstadoRegistroGuiaAereea.OBSERVADO, GuiaAereaDataGrid.estado_registro_codigo != Constantes.EstadoRegistroGuiaAereea.RECHAZADO))
        if  Constantes.Vista.GUIA_AEREA_REGISTROS_SUBSANAR == request.vistaCodigo:
            filters.append(or_(GuiaAereaDataGrid.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO, GuiaAereaDataGrid.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.RECHAZADO))

        if request.palabraClave:
            term = f"%{request.palabraClave.upper()}%"
            filters.append(or_(
                GuiaAereaDataGrid.numero.ilike(term),
                GuiaAereaDataGrid.origen_codigo.ilike(term),
                GuiaAereaDataGrid.destino_codigo.ilike(term),
                GuiaAereaDataGrid.nombre_remitente.ilike(term),
                GuiaAereaDataGrid.nombre_consignatario.ilike(term)
            ))
            
        if request.numero:
            filters.append(GuiaAereaDataGrid.numero.ilike(f"%{request.numero.upper()}%"))
        if request.origenCodigo:
            filters.append(GuiaAereaDataGrid.origen_codigo.ilike(f"%{request.origenCodigo.upper()}%"))
        if request.destinoCodigo:
            filters.append(GuiaAereaDataGrid.destino_codigo.ilike(f"%{request.destinoCodigo.upper()}%"))
        if request.transbordo:
             filters.append(GuiaAereaDataGrid.transbordo.ilike(f"%{request.transbordo.upper()}%"))
        if request.nombreRemitente:
             filters.append(GuiaAereaDataGrid.nombre_remitente.ilike(f"%{request.nombreRemitente.upper()}%"))
        if request.nombreConsignatario:
             filters.append(GuiaAereaDataGrid.nombre_consignatario.ilike(f"%{request.nombreConsignatario.upper()}%"))
        if request.habilitado is not None:
             filters.append(GuiaAereaDataGrid.habilitado == request.habilitado)
        if request.fechaInicioRegistro:
             filters.append(GuiaAereaDataGrid.fecha_consulta >= request.fechaInicioRegistro)
        if request.fechaFinRegistro:
             filters.append(GuiaAereaDataGrid.fecha_consulta <= request.fechaFinRegistro)
             
        data, total_count = await self.guia_aerea_filtro_repository.find_data_grid(
            filters=filters,
            start=request.start,
            limit=request.limit,
            sort=request.sort
        )
        return data, total_count


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
        doc.estado_confianza_codigo = Constantes.EstadoConfianza.AUTO_VALIDADO
        if not doc.estado_registro_codigo or doc.estado_registro_codigo != Constantes.EstadoRegistroGuiaAereea.OBSERVADO:
            doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.PROCESADO
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
            
            import logging
            inner_logger = logging.getLogger(__name__)
            inner_logger.info(f"CONFIDENCE DEBUG: Doc {doc.numero}. Sum: {weighted_sum}. TotalWeightFound: {total_weight_found}. Details: {[(camel_to_snake_upper(c.nombre_campo.replace('.', '_')), getattr(Constantes.PesoCampoGuiaAerea, camel_to_snake_upper(c.nombre_campo.replace('.', '_')), 0.0), c.confidence_modelo) for c in doc.confianzas_extraccion]}")

            doc.confidence_total = weighted_sum 

            if doc.confidence_total < 0.95:
                doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
                obs = f" Nivel de confianza ponderado insuficiente ({doc.confidence_total:.2%}). Se requiere revisión manual. "
                doc.observaciones = (doc.observaciones or "") + obs + "\n"
    async def _validar_duplicados(self, doc: GuiaAerea):
        duplicado = await self.document_repository.find_by_numero(doc.numero, str(doc.guia_aerea_id))
        if duplicado:
            doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            obs = f" Número de guía duplicado. Ya existe en la guía con ID {duplicado.guia_aerea_id}. "
            doc.observaciones = (doc.observaciones or "") + obs + "\n"
    async def _validar_numero_formato(self, doc: GuiaAerea):
        pattern = r"^\d{3}-\d{8}$"
        if  doc.numero and re.match(pattern, doc.numero):
            doc.tipo_codigo = Constantes.TipoGuiaAerea.MAESTRA
        else:
            doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            obs = " Formato de número de guía inválido (No cumple formato MAWB: XXX-XXXXXXXX). "
            doc.observaciones = (doc.observaciones or "") + obs
