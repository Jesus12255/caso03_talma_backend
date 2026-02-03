
from dto.guia_aerea_dtos import DeleteAllGuiaAereaRequest
from app.core.services.notificacion_service import NotificacionService
from core.realtime.publisher import publish_user_notification
from typing import List
from uuid import UUID

from app.core.domain.confianza_extraccion import ConfianzaExtraccion
from app.core.domain.guia_aerea import  GuiaAerea
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from app.core.repository.confianza_extraccion_repository import ConfianzaExtraccionRepository
from app.core.repository.document_repository import DocumentRepository
from app.core.repository.guia_aerea_filtro_repository import GuiaAereaFiltroRepository
from app.core.services.confianza_extraccion_service import ConfianzaExtraccionService
from app.core.services.document_service import DocumentService
from app.core.services.guia_aerea_interviniente_service import GuiaAereaIntervinienteService
from app.core.services.interviniente_service import IntervinienteService
from config.mapper import Mapper
from core.exceptions import AppBaseException
from core.service.service_base import ServiceBase
from dto.confianza_extraccion_dtos import GuiaAereaConfianzaRequest
from dto.guia_aerea_dtos import  GuiaAereaFiltroRequest, GuiaAereaRequest, GuiaAereaSubsanarRequest
from utl.constantes import Constantes
from utl.date_util import DateUtil
import re
from sqlalchemy import or_, and_
import logging
from core.realtime.publisher import publish_document_update

logger = logging.getLogger(__name__)

class DocumentServiceImpl(DocumentService, ServiceBase):

    def __init__(self, document_repository: DocumentRepository, guia_aerea_filtro_repository:GuiaAereaFiltroRepository , interviniente_service: IntervinienteService, confianza_extraccion_service: ConfianzaExtraccionService, confianza_extraccion_repository : ConfianzaExtraccionRepository, guia_aerea_interviniente_service: GuiaAereaIntervinienteService, notificacion_service: NotificacionService):
        self.document_repository = document_repository
        self.guia_aerea_filtro_repository = guia_aerea_filtro_repository
        self.interviniente_service = interviniente_service
        self.confianza_extraccion_service = confianza_extraccion_service
        self.confianza_extraccion_repository = confianza_extraccion_repository
        self.guia_aerea_interviniente_service = guia_aerea_interviniente_service
        self.notificacion_service = notificacion_service

    async def saveOrUpdate(self, t: GuiaAereaRequest):
        documento = None
        documento = Mapper.to_entity(t, GuiaAerea)
        documento.habilitado = Constantes.HABILITADO
        documento.creado = DateUtil.get_current_local_datetime()
        documento.creado_por = self.session.full_name
        documento.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.PROCESANDO
        await self.document_repository.save(documento)
        t.guiaAereaId = documento.guia_aerea_id
        
        await publish_document_update("INFO", f"Documento N°{documento.numero} guardado, procesando información adicional", documento.guia_aerea_id)
        t.guiaAereaId = documento.guia_aerea_id
            

    async def save_all_confianza_extraccion(self, t: GuiaAereaRequest):
        confianzas_extraccion = []
        for confianza in t.confianzas:
            if "." not in confianza.nombreCampo:
                confianza_extraccion = ConfianzaExtraccion()
                confianza_extraccion.entidad_tipo = "GUIA_AEREA"
                confianza_extraccion.entidad_id = t.guiaAereaId
                confianza_extraccion.nombre_campo = confianza.nombreCampo
                confianza_extraccion.valor_extraido = confianza.valorExtraido
                confianza_extraccion.confidence_modelo = confianza.confidenceModelo
                confianza_extraccion.habilitado = Constantes.HABILITADO
                confianza_extraccion.creado = DateUtil.get_current_local_datetime()
                confianza_extraccion.creado_por = Constantes.SYSTEM_USER
                confianzas_extraccion.append(confianza_extraccion)
                confianza.guiaAereaId = t.guiaAereaId
        await self.confianza_extraccion_repository.save_all(confianzas_extraccion)

    
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
        filters.append(GuiaAereaDataGrid.) 
             
        data, total_count = await self.guia_aerea_filtro_repository.find_data_grid(
            filters=filters,
            start=request.start,
            limit=request.limit,
            sort=request.sort
        )
        return data, total_count

    async def get(self, documentoId: str) -> GuiaAerea:
        documento = await self.document_repository.get_by_id(documentoId)
        if documento is not None:
            return documento
        raise AppBaseException("El documento no se encuentra registrado")

    async def updateAndReprocess(self, t: GuiaAereaSubsanarRequest):
        guia_aerea = await self.get(t.guiaAereaId)
        guia_aerea.guia_aerea_id = t.guiaAereaId
        guia_aerea.numero = t.numero
        guia_aerea.confidence_numero = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.fecha_emision = t.fechaEmision
        guia_aerea.confidence_fecha_emision = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.origen_codigo = t.origenCodigo
        guia_aerea.confidence_origen_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.destino_codigo = t.destinoCodigo
        guia_aerea.confidence_destino_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.transbordo = t.transbordo
        guia_aerea.confidence_transbordo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.aerolinea_codigo = t.aerolineaCodigo
        guia_aerea.confidence_aerolinea_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.numero_vuelo = t.numeroVuelo
        guia_aerea.confidence_numero_vuelo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.fecha_vuelo = t.fechaVuelo
        guia_aerea.confidence_fecha_vuelo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.descripcion_mercancia = t.descripcionMercancia
        guia_aerea.confidence_descripcion_mercancia = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.cantidad_piezas = t.cantidadPiezas
        guia_aerea.confidence_cantidad_piezas = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.peso_bruto = t.pesoBruto
        guia_aerea.confidence_peso_bruto = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.peso_cobrado = t.pesoCobrado
        guia_aerea.confidence_peso_cobrado = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.unidad_peso_codigo = t.unidadPesoCodigo
        guia_aerea.confidence_unidad_peso_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.volumen = t.volumen
        guia_aerea.confidence_volumen = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.naturaleza_carga_codigo = t.naturalezaCargaCodigo
        guia_aerea.confidence_naturaleza_carga_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.valor_declarado = t.valorDeclarado
        guia_aerea.confidence_valor_declarado = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.tipo_flete_codigo = t.tipoFleteCodigo
        guia_aerea.confidence_tipo_flete_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.tarifa_flete = t.tarifaFlete
        guia_aerea.confidence_tarifa_flete = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.otros_cargos = t.otrosCargos
        guia_aerea.confidence_otros_cargos = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.moneda_codigo = t.monedaCodigo
        guia_aerea.confidence_moneda_codigo = Constantes.VALIDATE_MANUAL_CONFIDENCE
        
        guia_aerea.total_flete = t.totalFlete
        guia_aerea.confidence_total_flete = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.instrucciones_especiales = t.instruccionesEspeciales
        guia_aerea.confidence_instrucciones_especiales = Constantes.VALIDATE_MANUAL_CONFIDENCE

        guia_aerea.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.PROCESADO

        await self._validar_duplicados(guia_aerea)
        await self._validar_numero_formato(guia_aerea)

        if Constantes.EstadoRegistroGuiaAereea.PROCESADO == guia_aerea.estado_registro_codigo:
            guia_aerea.confidence_total = Constantes.VALIDATE_MANUAL_CONFIDENCE
            guia_aerea.estado_confianza_codigo = Constantes.EstadoConfianza.REVISION_MANUAL
            guia_aerea.observaciones = Constantes.EMPTY
            
            guia_aerea.modificado = DateUtil.get_current_local_datetime()
            guia_aerea.modificado_por = self.session.full_name
            
            await self.document_repository.save(guia_aerea)
            await publish_user_notification(str(self.session.user_id), "INFO", f"Guía aérea N°{t.numero}: Actualizado correctamente! Procesando información adicional", str(t.guiaAereaId))
            await self.guia_aerea_interviniente_service.saveAndReprocess(t)
            await publish_user_notification(str(self.session.user_id), "INFO", f"Guía aérea N°{t.numero}: Información adicional procesada correctamente!", str(t.guiaAereaId))
            await publish_user_notification(str(self.session.user_id), "SUCCESS", f"Guía aérea N°{t.numero}: Proceso de actualización finalizado correctamente.", str(t.guiaAereaId))

            await self.notificacion_service.resolver(guia_aerea.guia_aerea_id)
           
        return guia_aerea


    async def get_with_relations(self, documentoId: str):
        documento = await self.document_repository.get_by_id_with_relations(documentoId)
        if documento is not None:
            return documento
        raise AppBaseException("El documento no se encuentra registrado")

    async def reprocess(self, document_id: str):
        # 1. Get Document with relations
        doc = await self.get_with_relations(document_id)
        if not doc:
             raise AppBaseException("Documento no encontrado")
        
        # 2. Recalculate Confidence (Mature Model Logic)
        #await self.confianza_extraccion_service.calculate_total_confidence(doc)
        
        # 3. Update Status
        if doc.confidence_total and doc.confidence_total >= 0.95:
             doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.PROCESADO
             doc.estado_confianza_codigo = Constantes.EstadoConfianza.AUTO_VALIDADO
        else:
             doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
             doc.estado_confianza_codigo = Constantes.EstadoConfianza.REVISION_MANUAL
        
        doc.modificado = DateUtil.get_current_local_datetime()
        doc.modificado_por = self.session.full_name
        
        await self.document_repository.save(doc)
        return True


    async def apply_business_rules(self, doc: GuiaAereaRequest) -> GuiaAerea:
        guia_aerea = await self.get(doc.guiaAereaId)

        # 1️⃣ Precargar intervinientes
        intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(
            guia_aerea.guia_aerea_id
        )

        intervinientes_map = {
            i.guia_aerea_interviniente_id: i
            for i in intervinientes
        }

        intervinientes_modificados = set()

        # 2️⃣ Validaciones (sin IO)
        await self._validar_confiabilidad(
            doc,
            guia_aerea,
            intervinientes_map,
            intervinientes_modificados
        )
        await self._validar_duplicados(guia_aerea)
        await self._validar_numero_formato(guia_aerea)

        # 3️⃣ Estado final coherente
        guia_aerea.modificado = DateUtil.get_current_local_datetime()
        guia_aerea.modificado_por = Constantes.SYSTEM_USER

        if guia_aerea.confidence_total >= 0.95:
            guia_aerea.estado_confianza_codigo = Constantes.EstadoConfianza.AUTO_VALIDADO
        else:
            guia_aerea.estado_confianza_codigo = Constantes.EstadoConfianza.REVISION_MANUAL

        if guia_aerea.estado_registro_codigo != Constantes.EstadoRegistroGuiaAereea.OBSERVADO:
            guia_aerea.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.PROCESADO

        # 4️⃣ Persistencia
        await self.document_repository.save(guia_aerea)

        for interviniente in intervinientes_modificados:
            await self.guia_aerea_interviniente_service.update(interviniente)

        return guia_aerea

    # -------------------------------------------------------------------------
    # VALIDAR CONFIABILIDAD (SIN BD)
    # -------------------------------------------------------------------------
    async def _validar_confiabilidad(
        self,
        guia_aerea_request: GuiaAereaRequest,
        guia_aerea: GuiaAerea,
        intervinientes_map: dict,
        intervinientes_modificados: set
    ):
        if not guia_aerea_request.confianzas:
            return

        suma_ponderada = 0.0
        peso_total = 0.0

        def camel_to_snake_upper(name: str) -> str:
            s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

        for confianza in guia_aerea_request.confianzas:
            if not confianza:
                continue

            clave = camel_to_snake_upper(confianza.nombreCampo.replace(".", "_"))
            peso = getattr(Constantes.PesoCampoGuiaAerea, clave, 0.0)

            if confianza.valorExtraido is not None and peso > 0:
                suma_ponderada += confianza.confidenceModelo * peso
                peso_total += peso

            self._guardar_confianza_valida(
                confianza,
                guia_aerea,
                intervinientes_map,
                intervinientes_modificados
            )

        guia_aerea.confidence_total = (
            round(suma_ponderada / peso_total, 4) if peso_total > 0 else 0.0
        )

        if guia_aerea.confidence_total < 0.95:
            guia_aerea.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            guia_aerea.observaciones = (
                (guia_aerea.observaciones or "") +
                f" Nivel de confianza insuficiente ({guia_aerea.confidence_total:.2%}).\n"
            )

    # -------------------------------------------------------------------------
    # GUARDAR CONFIANZA (EN MEMORIA)
    # -------------------------------------------------------------------------
    def _guardar_confianza_valida(
        self,
        datos_confianza: GuiaAereaConfianzaRequest,
        guia_aerea: GuiaAerea,
        intervinientes_map: dict,
        intervinientes_modificados: set
    ):
        if datos_confianza.confidenceModelo < 0.95:
            return

        def camel_to_snake(name: str) -> str:
            s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        campo = datos_confianza.nombreCampo.split(".")[-1]

        if datos_confianza.intervinienteId and "." in datos_confianza.nombreCampo:
            interviniente = intervinientes_map.get(datos_confianza.intervinienteId)
            if not interviniente:
                return

            conf_field = f"confidence_{camel_to_snake(campo)}"

            if hasattr(interviniente, conf_field):
                setattr(interviniente, conf_field, datos_confianza.confidenceModelo)
                interviniente.modificado = DateUtil.get_current_local_datetime()
                interviniente.modificado_por = Constantes.SYSTEM_USER
                intervinientes_modificados.add(interviniente)

        else:
            conf_field = f"confidence_{camel_to_snake(campo)}"
            if hasattr(guia_aerea, conf_field):
                setattr(guia_aerea, conf_field, datos_confianza.confidenceModelo)

     


    async def _validar_duplicados(self, doc: GuiaAerea):
        duplicado = await self.document_repository.find_by_numero(doc.numero, str(doc.guia_aerea_id))
        if duplicado:
            doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            obs = " Número de guía duplicado. "
            doc.observaciones = (doc.observaciones or "") + obs + "\n"
            await publish_document_update("WARNING", f"Guía aérea N°{doc.numero}: Número de guía aérea duplicado", doc.guia_aerea_id)
            if hasattr(self, 'session') and self.session and self.session.user_id:
                 await publish_user_notification(str(self.session.user_id), "WARNING", f"Guía aérea N°{doc.numero}: Número de guía aérea duplicado", str(doc.guia_aerea_id), title="Validación Fallida", severity="WARNING")

    async def _validar_numero_formato(self, doc: GuiaAerea):
        pattern = r"^\d{3}-\d{8}$"
        clean_num = doc.numero.replace(" ", "") if doc.numero else ""
        
        if  clean_num and re.match(pattern, clean_num):
            doc.numero = clean_num # Auto-fix the format
            doc.tipo_codigo = Constantes.TipoGuiaAerea.MAESTRA
        else:
            doc.estado_registro_codigo = Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            obs = " Formato de número de guía inválido (No cumple formato MAWB: XXX-XXXXXXXX). "
            doc.observaciones = (doc.observaciones or "") + obs
            await publish_document_update("WARNING", f"Guía aérea N°{doc.numero}: Número de guía aérea sin formato válido", doc.guia_aerea_id)
            if hasattr(self, 'session') and self.session and self.session.user_id:
                 await publish_user_notification(str(self.session.user_id), "WARNING", f"Guía aérea N°{doc.numero}: Número de guía aérea sin formato válido", str(doc.guia_aerea_id), title="Validación Fallida", severity="WARNING")

    async def delete(self, guia_aerea_id: UUID):
        guia_aerea = await self.get(str(guia_aerea_id))
        if Constantes.HABILITADO == guia_aerea.habilitado:
            guia_aerea.habilitado = Constantes.INHABILITADO
        else:
            guia_aerea.habilitado = Constantes.HABILITADO
        guia_aerea.modificado = DateUtil.get_current_local_datetime()
        guia_aerea.modificado_por = self.session.full_name
        await self.document_repository.save(guia_aerea)

    async def deleteAll(self, request: DeleteAllGuiaAereaRequest):
        for id in request.guiaAereaIds:
            await self.delete(id)