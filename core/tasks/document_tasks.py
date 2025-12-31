import asyncio
import logging
import json
import redis.asyncio as redis
from app.core.celery_app import celery_app
from config.database_config import AsyncSessionLocal
from config.config import settings
from utl.constantes import Constantes
from utl.date_util import DateUtil

# Repositories & Services
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.repository.impl.interviniente_repository_impl import IntervinienteRepositoryImpl
from app.core.repository.impl.confianza_extraccion_repository_impl import ConfianzaExtraccionRepositoryImpl

from app.core.services.impl.document_service_impl import DocumentServiceImpl
from app.core.services.impl.interviniente_service_impl import IntervinienteServiceImpl
from app.core.services.impl.confianza_extraccion_service_impl import ConfianzaExtraccionServiceImpl

logger = logging.getLogger(__name__)

async def _process_validations_async(guia_aerea_id: str):
    async with AsyncSessionLocal() as db:
        try:

            from app.core.repository.impl.guia_aerea_filtro_repository_impl import GuiaAereaFiltroRepositoryImpl
            
            doc_repo = DocumentRepositoryImpl(db)
            filtro_repo = GuiaAereaFiltroRepositoryImpl(db)
            int_repo = IntervinienteRepositoryImpl(db)
            conf_repo = ConfianzaExtraccionRepositoryImpl(db)
            
            int_service = IntervinienteServiceImpl(int_repo)
            conf_service = ConfianzaExtraccionServiceImpl(conf_repo)
            
            doc_service = DocumentServiceImpl(doc_repo, filtro_repo, int_service, conf_service)
            
            doc = await doc_service.get_with_relations(guia_aerea_id)     
            await doc_service.apply_business_rules(doc)
            
            logger.info(f"Documento {guia_aerea_id} procesado. Estado: {doc.estado_registro_codigo}")
            
            if doc:
                redis_client = redis.from_url(settings.REDIS_URL)
                msg = {
                    "guia_aerea_id": str(guia_aerea_id),
                    "estado_registro_codigo": doc.estado_registro_codigo,
                    "estado_guia_codigo": doc.estado_guia_codigo,
                    "tipo_codigo": doc.tipo_codigo,
                    "mensaje": "Validación completada en segundo plano"
                }
                await redis_client.publish("document_updates", json.dumps(msg))
                await redis_client.close()

        except Exception as e:
            logger.error(f"Error procesando documento {guia_aerea_id}: {e}")

@celery_app.task(name="core.tasks.document_tasks.process_document_validations")
def process_document_validations(guia_aerea_id: str):
    asyncio.run(_process_validations_async(guia_aerea_id))
