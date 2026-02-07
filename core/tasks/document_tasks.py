from dto.notificacion import NotificacionRequest
from app.core.services.impl.notificacion_service_impl import NotificacionServiceImpl
from app.core.repository.impl.notificacion_repository_impl import NotificacionRepositoryImpl
import asyncio
import logging
import json
import uuid
from core.celery.celery_app import celery_app
from app.core.repository.impl.guia_aerea_filtro_repository_impl import GuiaAereaFiltroRepositoryImpl
from app.core.repository.impl.guia_aerea_interviniente_repository_impl import GuiaAereaIntervinienteRepositoryImpl
from app.core.services.impl.guia_aerea_interviniente_service_impl import GuiaAereaIntervinienteServiceImpl
from config.database_config import AsyncSessionLocal
from config.config import settings
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.repository.impl.interviniente_repository_impl import IntervinienteRepositoryImpl
from app.core.repository.impl.confianza_extraccion_repository_impl import ConfianzaExtraccionRepositoryImpl
from app.core.services.impl.document_service_impl import DocumentServiceImpl
from app.core.services.impl.interviniente_service_impl import IntervinienteServiceImpl
from app.core.services.impl.confianza_extraccion_service_impl import ConfianzaExtraccionServiceImpl
from dto.guia_aerea_dtos import GuiaAereaRequest
from core.realtime.publisher import publish_document_update, publish_user_notification
from utl.constantes import Constantes

logger = logging.getLogger(__name__)

async def _process_validations_async(obj_req: str):
    async with AsyncSessionLocal() as db:
        t = None
        try:
            t = GuiaAereaRequest.model_validate(json.loads(obj_req)) 
            from utl.date_util import DateUtil 
 
            from app.core.repository.impl.manifiesto_repository_impl import ManifiestoRepositoryImpl
            from app.core.services.impl.manifiesto_service_impl import ManifiestoServiceImpl
            
            manifiesto_repository = ManifiestoRepositoryImpl(db)
            notificacion_repository = NotificacionRepositoryImpl(db)
            notificacion_service = NotificacionServiceImpl(notificacion_repository)
            
            guia_aerea_interviniente_repository = GuiaAereaIntervinienteRepositoryImpl(db)
            confianza_extraccion_repository = ConfianzaExtraccionRepositoryImpl(db)
            guia_aerea_interviniente_service = GuiaAereaIntervinienteServiceImpl(guia_aerea_interviniente_repository, confianza_extraccion_repository)
            
            guia_aerea_repository = DocumentRepositoryImpl(db)
            guia_aerea_filtro_repository = GuiaAereaFiltroRepositoryImpl(db)
            interviniente_repository = IntervinienteRepositoryImpl(db)
            interviniente_service = IntervinienteServiceImpl(interviniente_repository)
            conf_service = ConfianzaExtraccionServiceImpl(confianza_extraccion_repository)

            guia_aerea_service = DocumentServiceImpl(guia_aerea_repository, guia_aerea_filtro_repository, interviniente_service, conf_service, confianza_extraccion_repository, guia_aerea_interviniente_service, notificacion_service, manifiesto_repository)
            
            manifiesto_service = ManifiestoServiceImpl(manifiesto_repository, guia_aerea_service)
            
            
            
            await guia_aerea_service.save_all_confianza_extraccion(t)
            # Removed duplicate call
            await publish_user_notification(str(t.usuarioId), "INFO", f"Guía aérea N°{t.numero}: Confianzas recibidas", str(t.guiaAereaId))

            await guia_aerea_interviniente_service.save(t)
            await publish_user_notification(str(t.usuarioId), "INFO", f"Guía aérea N°{t.numero}: Intervinientes recibidos", str(t.guiaAereaId))

            doc = await guia_aerea_service.apply_business_rules(t)
            logger.info(f"Documento {t.guiaAereaId} procesado. Estado: {doc.estado_registro_codigo}")

            if doc:
                if Constantes.EstadoRegistroGuiaAereea.OBSERVADO != doc.estado_registro_codigo : 
                    await manifiesto_service.associate_guia(doc)
                    await publish_user_notification(str(t.usuarioId), "SUCCESS", f"Guía aérea N°{t.numero}: Procesado correctamente", str(t.guiaAereaId))
                else:
                    logger.info(f"Documento Observado. Creando notificación para usuario {t.usuarioId}...")
                    notificacion_request = NotificacionRequest(
                        notificacionId=uuid.uuid4(),
                        guiaAereaId=t.guiaAereaId,
                        usuarioId=t.usuarioId,
                        tipoCodigo=Constantes.TipoNotificacion.OBSERVACION,
                        titulo="Guía Aérea Observada",
                        mensaje=f"Guía aérea N°{t.numero}: Observado, favor de corregir",
                        severidadCodigo=Constantes.SeveridadNotificacion.CRITICAL
                    )
                    await notificacion_service.save(notificacion_request)

        except Exception as e:
            doc_id = t.guiaAereaId if t else "Desconocido"
            logger.error(f"Error procesando documento {doc_id}: {e}")

@celery_app.task(name="core.tasks.document_tasks.process_document_validations")
def process_document_validations(obj_req: str):
    asyncio.run(_process_validations_async(obj_req))
