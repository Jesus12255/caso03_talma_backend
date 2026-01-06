import asyncio
import sys
import os
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

# Add the project root to sys.path
sys.path.append(os.getcwd())

from config.database_config import engine, AsyncSessionLocal
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.repository.impl.interviniente_repository_impl import IntervinienteRepositoryImpl
from app.core.repository.impl.confianza_extraccion_repository_impl import ConfianzaExtraccionRepositoryImpl
from app.core.services.impl.document_service_impl import DocumentServiceImpl
from app.core.services.impl.interviniente_service_impl import IntervinienteServiceImpl
from app.core.services.impl.confianza_extraccion_service_impl import ConfianzaExtraccionServiceImpl
from dto.guia_aerea_dtos import GuiaAereaRequest
from dto.interviniente_dtos import IntervinienteRequest
from dto.confianza_extraccion_dtos import GuiaAereaConfianzaRequest
from app.core.context.user_context import set_user_session, UserSession

async def verify_save_flow():
    print("Starting Guia Aerea Save Verification...")
    
    async_session = AsyncSessionLocal
    
    async with async_session() as session:
        # Set User Session
        set_user_session(UserSession(full_name='Test User'))

        # Initialize Repositories
        doc_repo = DocumentRepositoryImpl(session)
        int_repo = IntervinienteRepositoryImpl(session)
        conf_repo = ConfianzaExtraccionRepositoryImpl(session)
        
        # Initialize Services
        int_service = IntervinienteServiceImpl(int_repo)
        conf_service = ConfianzaExtraccionServiceImpl(conf_repo)
        doc_service = DocumentServiceImpl(doc_repo, int_service, conf_service)
        
        # Construct Request
        intervinientes = [
            IntervinienteRequest(
                nombre="Remitente Test",
                tipo_codigo="REMITENTE",
                direccion="Av. Test 123",
                pais_codigo="PE"
            ),
            IntervinienteRequest(
                nombre="Consignatario Test",
                tipo_codigo="CONSIGNATARIO",
                direccion="Av. Test 456",
                pais_codigo="PE"
            )
        ]
        
        confianzas = []
        for i in range(42):
            confianzas.append(GuiaAereaConfianzaRequest(
                nombreCampo=f"campo_{i}",
                confidenceModelo=0.99,
                confidenceFinal=0.99,
                valorExtraido="test_val",
                valorFinal="test_val"
            ))
            
        request = GuiaAereaRequest(
            intervinientes=intervinientes,
            numero=f"TEST-{uuid.uuid4().hex[:6].upper()}",
            tipoCodigo="MASTER",
            fechaEmision=datetime.now(),
            estadoGuiaCodigo="ACTIVO",
            origenCodigo="LIM",
            destinoCodigo="MIA",
            cantidadPiezas=10,
            monedaCodigo="USD",
            totalFlete=Decimal("100.50"),
            estadoRegistroCodigo="VALIDO",
            confianzas=confianzas
        )
        
        print("Saving document...")
        try:
            await doc_service.saveOrUpdate(request)
            print("Document saved successfully!")
            
            # Verify if confianzas were saved (basic check via print, or query)
            # In a real test we would query back, but success here implies no exception.
            print(f"Assign GuiaAereaID: {request.guiaAereaId}")
            
        except Exception as e:
            print(f"Error saving document: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_save_flow())
