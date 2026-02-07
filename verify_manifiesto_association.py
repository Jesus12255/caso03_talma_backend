import asyncio
import sys
import os
import uuid
from decimal import Decimal
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.getcwd())

from config.database_config import AsyncSessionLocal
from app.core.repository.impl.manifiesto_repository_impl import ManifiestoRepositoryImpl
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.services.impl.manifiesto_service_impl import ManifiestoServiceImpl
from app.core.domain.guia_aerea import GuiaAerea
from app.core.domain.manifiesto import Manifiesto
from utl.constantes import Constantes
from core.context.user_context import set_user_session, UserSession
from app.security.domain.Usuario import Usuario
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente

async def verify_manifiesto_association():
    print("Starting Manifiesto Association Verification...")
    
    async with AsyncSessionLocal() as session:
        # Set Global User Session
        set_user_session(UserSession(full_name='Test User', user_id=uuid.uuid4(), role_code='OPERADOR'))

        # Repositories
        manifiesto_repo = ManifiestoRepositoryImpl(session)
        document_repo = DocumentRepositoryImpl(session)
        
        # Simplified DocumentService for testing
        class SimpleDocumentService:
            def __init__(self, repo):
                 self.document_repository = repo
                 # We can simulate session access if needed, or just rely on global context if we were using real service
                 # But here we are mocking, so we can property set it if we want, or just ignore.
                 # DocumentServiceImpl uses self.session. So if we Mock it, we can define it.
                 self.session = UserSession(full_name='Test User', user_id=uuid.uuid4(), role_code='OPERADOR')
                 
            async def get(self, id):
                # We need to return a GuiaAerea entity
                return await self.document_repository.get_by_id(id)

            async def setManifiesto(self, manifiesto_id, guia_aerea_id):
                 guia = await self.get(str(guia_aerea_id))
                 guia.manifiesto_id = manifiesto_id
                 await self.document_repository.save(guia)

        simple_doc_service = SimpleDocumentService(document_repo)
        
        manifiesto_service = ManifiestoServiceImpl(manifiesto_repo, simple_doc_service)
        # Note: ManifiestoService gets session from context via ServiceBase

        print("1. Creating Test Guia Aerea...")
        unique_flight = f"FL-{uuid.uuid4().hex[:6].upper()}"
        unique_date = datetime.now()
        
        guia = GuiaAerea(
            guia_aerea_id = uuid.uuid4(),
            numero = f"999-{uuid.uuid4().hex[:8].upper()}",
            numero_vuelo = unique_flight,
            fecha_vuelo = unique_date,
            fecha_emision = unique_date,
            origen_codigo = "TEST_ORG",
            destino_codigo = "TEST_DST",
            cantidad_piezas = 10,
            peso_bruto = Decimal("100.00"),
            volumen = Decimal("1.5"),
            estado_registro_codigo = "VALIDO",
            moneda_codigo = "USD",
            total_flete = Decimal("0"),
            habilitado = True
        )
        await document_repo.save(guia)
        
        print(f"   Guia ID: {guia.guia_aerea_id}")
        
        print("2. associating Guia to Manifiesto (First Time)...")
        await manifiesto_service.associate_guia(guia)
        
        # Verify Manifiesto Created
        manifiesto = await manifiesto_repo.find_by_vuelo_fecha(unique_flight, unique_date)
        if not manifiesto:
            print("ERROR: Manifiesto not created!")
            return

        print(f"   Manifiesto Created ID: {manifiesto.manifiesto_id}")
        print(f"   Total Guias: {manifiesto.total_guias} (Expected 1)")
        print(f"   Total Bultos: {manifiesto.total_bultos} (Expected 10)")
        
        if manifiesto.total_guias != 1 or manifiesto.total_bultos != 10:
             print("ERROR: Totals are incorrect!")

        # Verify Link
        guia_reloaded = await document_repo.get_by_id(str(guia.guia_aerea_id))
        if guia_reloaded.manifiesto_id != manifiesto.manifiesto_id:
             print(f"ERROR: Guia not linked! {guia_reloaded.manifiesto_id}")
        else:
             print("   Guia linked successfully.")

        print("3. Testing Idempotency (Calling associate_guia again)...")
        await manifiesto_service.associate_guia(guia)
        
        # Verify Totals Unchanged
        await session.refresh(manifiesto)
        
        print(f"   Total Guias: {manifiesto.total_guias} (Expected 1)")
        print(f"   Total Bultos: {manifiesto.total_bultos} (Expected 10)")
        
        if manifiesto.total_guias != 1:
            print("ERROR: Idempotency Failed! Total Guias increased.")
        else:
            print("   Idempotency Verified.")

        print("4. Associates Second Guia to Same Manifiesto...")
        guia2 = GuiaAerea(
            guia_aerea_id = uuid.uuid4(),
            numero = f"999-{uuid.uuid4().hex[:8].upper()}",
            numero_vuelo = unique_flight,
            fecha_vuelo = unique_date,
            fecha_emision = unique_date,
            origen_codigo = "TEST_ORG",
            destino_codigo = "TEST_DST",
            cantidad_piezas = 5,
            peso_bruto = Decimal("50.00"),
            estado_registro_codigo = "VALIDO",
             moneda_codigo = "USD",
            total_flete = Decimal("0"),
            habilitado = True
        )
        await document_repo.save(guia2)
        await manifiesto_service.associate_guia(guia2)
        
        await session.refresh(manifiesto)
        print(f"   Total Guias: {manifiesto.total_guias} (Expected 2)")
        print(f"   Total Bultos: {manifiesto.total_bultos} (Expected 15)")

        if manifiesto.total_guias == 2 and manifiesto.total_bultos == 15:
             print("SUCCESS: Manifiesto workflow verification passed!")
        else:
             print("ERROR: Totals incorrect after second guia.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_manifiesto_association())
