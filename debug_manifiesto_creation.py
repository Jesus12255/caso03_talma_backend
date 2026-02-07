
import asyncio
import sys
import os
import uuid
from decimal import Decimal

# Ensure project root is in python path
sys.path.append(os.getcwd())

from config.database_config import AsyncSessionLocal
from app.core.repository.impl.manifiesto_repository_impl import ManifiestoRepositoryImpl
from app.core.services.impl.manifiesto_service_impl import ManifiestoServiceImpl
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.services.impl.document_service_impl import DocumentServiceImpl
from app.core.repository.impl.guia_aerea_filtro_repository_impl import GuiaAereaFiltroRepositoryImpl
from app.core.repository.impl.interviniente_repository_impl import IntervinienteRepositoryImpl
from app.core.services.impl.interviniente_service_impl import IntervinienteServiceImpl
from app.core.repository.impl.confianza_extraccion_repository_impl import ConfianzaExtraccionRepositoryImpl
from app.core.services.impl.confianza_extraccion_service_impl import ConfianzaExtraccionServiceImpl
from app.core.repository.impl.guia_aerea_interviniente_repository_impl import GuiaAereaIntervinienteRepositoryImpl
from app.core.services.impl.guia_aerea_interviniente_service_impl import GuiaAereaIntervinienteServiceImpl
from app.core.repository.impl.notificacion_repository_impl import NotificacionRepositoryImpl
from app.core.services.impl.notificacion_service_impl import NotificacionServiceImpl
from utl.constantes import Constantes

# Explicit import for registry
from app.core.domain.guia_aerea import GuiaAerea
from app.core.domain.manifiesto import Manifiesto

TARGET_GUIA_ID = "90fe07de-2b14-43db-8a99-c1c64acf3297"

async def debug_association():
    print(f"Starting debug for Guia ID: {TARGET_GUIA_ID}")
    
    async with AsyncSessionLocal() as db:
        try:
            # Initialize all services as in document_tasks.py
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
            
            guia_aerea_service = DocumentServiceImpl(guia_aerea_repository, guia_aerea_filtro_repository, interviniente_service, conf_service, confianza_extraccion_repository, guia_aerea_interviniente_service, notificacion_service)
            
            manifiesto_repository = ManifiestoRepositoryImpl(db)
            manifiesto_service = ManifiestoServiceImpl(manifiesto_repository, guia_aerea_service)
            
            # Fetch the document
            print("Fetching document...")
            doc = await guia_aerea_service.get(TARGET_GUIA_ID)
            print(f"Document found: {doc.numero}")
            print(f"Vuelo: {doc.numero_vuelo}, Fecha: {doc.fecha_vuelo}")
            print(f"Current Manifiesto ID: {doc.manifiesto_id}")
            
            # Attempt association
            print("Calling associate_guia...")
            await manifiesto_service.associate_guia(doc)
            print("associate_guia completed.")
            
            # Verify result
            print("Refetching document...")
            doc_updated = await guia_aerea_service.get(TARGET_GUIA_ID)
            print(f"Updated Manifiesto ID: {doc_updated.manifiesto_id}")
            
            if doc_updated.manifiesto_id:
                print("SUCCESS: Manifiesto linked.")
                # Basic Manifest check
                man = await manifiesto_repository.get_by_id(doc_updated.manifiesto_id)
                print(f"Manifiesto details: ID={man.manifiesto_id}, GuiaCount={man.total_guias}")
            else:
                print("FAILURE: Manifiesto ID is still None.")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_association())
