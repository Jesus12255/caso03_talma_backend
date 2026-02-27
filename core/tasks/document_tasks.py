from core.service.service_container import ServiceContainer
from dto.notificacion import NotificacionRequest
import asyncio
import logging
import json
import uuid
from core.celery.celery_app import celery_app
from dto.guia_aerea_dtos import GuiaAereaRequest
from core.realtime.publisher import  publish_user_notification
from utl.constantes import Constantes
from config.database_config import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def _process_validations_async(obj_req: str):
    async with AsyncSessionLocal() as db:
        t = None
        try:
            contenedor = ServiceContainer(db)
            t = GuiaAereaRequest.model_validate(json.loads(obj_req)) 

            await contenedor.guia_aerea_service.save_all_confianza_extraccion(t)
            await publish_user_notification(str(t.usuarioId), "INFO", f"Guía aérea N°{t.numero}: Confianzas recibidas", str(t.guiaAereaId))
            await contenedor.guia_aerea_interviniente_service.save(t)
            await publish_user_notification(str(t.usuarioId), "INFO", f"Guía aérea N°{t.numero}: Intervinientes recibidos", str(t.guiaAereaId))
            doc = await contenedor.guia_aerea_service.apply_business_rules(t)

            if Constantes.EstadoRegistroGuiaAereea.OBSERVADO == doc.estado_registro_codigo: 
                notificacion_request = NotificacionRequest(
                    notificacionId=uuid.uuid4(),
                    guiaAereaId=t.guiaAereaId,
                    usuarioId=t.usuarioId,
                    tipoCodigo=Constantes.TipoNotificacion.OBSERVACION,
                    titulo="Guía Aérea Observada",
                    mensaje=f"Guía aérea N°{t.numero}: Observado, favor de corregir",
                    severidadCodigo=Constantes.SeveridadNotificacion.CRITICAL
                )
                await contenedor.notificacion_service.save(notificacion_request)
                await contenedor.auditoria_service.registrar_modificacion(
                    entidad_tipo=Constantes.TipoEntidadAuditoria.GUIA_AEREA,
                    entidad_id=t.guiaAereaId,
                    numero_documento=t.numero,
                    campo="estado_registro_codigo",
                    valor_anterior="PROCESANDO",
                    valor_nuevo="OBSERVADO"
                )
                return
            
            
            await contenedor.irregularidad_service.detectar_irregularidades(doc, t.analisisContextual)
            
            doc_actualizado = await contenedor.guia_aerea_service.get(str(t.guiaAereaId))
            if doc_actualizado.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO:
                return

            await contenedor.manifiesto_service.associate_guia(doc)
           
            await contenedor.auditoria_service.registrar_modificacion(
                entidad_tipo=Constantes.TipoEntidadAuditoria.GUIA_AEREA,
                entidad_id=t.guiaAereaId,
                numero_documento=t.numero,
                campo="estado_registro_codigo",
                valor_anterior="PROCESANDO",
                valor_nuevo="PROCESADO"
            ) 
                       
        except Exception as e:
            doc_id = t.guiaAereaId if t else "Desconocido"
            logger.error(f"Error procesando documento {doc_id}: {e}")

@celery_app.task(name="core.tasks.document_tasks.process_document_validations")
def process_document_validations(obj_req: str):
    asyncio.run(_process_validations_async(obj_req))
