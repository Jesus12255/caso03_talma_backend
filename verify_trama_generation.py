import asyncio
import sys
import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

# Mock dependencies that might be missing in execution env
sys.modules["fastapi"] = MagicMock()
sys.modules["celery"] = MagicMock()

# Add paths to allow mixed imports (app.core... and core...)
cwd = os.getcwd()
sys.path.append(cwd)

from app.core.services.impl.trama_service_impl import TramaServiceImpl
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid

# Mock Repositories
class MockRepo:
    pass

async def verify_generation():
    print("Verifying Trama Generation logic...")
    # Initialize service with mock repos (not used for this test)
    service = TramaServiceImpl(MockRepo(), MockRepo())

    # Create Mock Data
    guias = [
        GuiaAereaDataGrid(
            numero="999-12345678",
            numero_vuelo="LA2500",
            fecha_vuelo=datetime.now(),
            origen_codigo="LIM",
            destino_codigo="MIA",
            cantidad_piezas=10,
            peso_bruto=Decimal("100.00"),
            volumen=Decimal("1.5"),
            descripcion_mercancia="GENERAL CARGO",
            naturaleza_carga_codigo="GEN"
        ),
        GuiaAereaDataGrid(
            numero="999-87654321",
            numero_vuelo="LA2500",
            fecha_vuelo=datetime.now(),
            origen_codigo="LIM",
            destino_codigo="MIA",
            cantidad_piezas=5,
            peso_bruto=Decimal("50.00"),
            volumen=Decimal("0.5"),
            descripcion_mercancia="PERISHABLE",
            naturaleza_carga_codigo="PER"
        )
    ]

    print("\n1. Testing validate_batch...")
    result = await service.validate_batch(guias)
    print("Result:", result)
    
    if result["status"] == "OK":
        print("SUCCESS: Batch validated correctly.")
        if result["resumen"]["total_guias"] == 2 and result["resumen"]["peso_total"] == 150.0:
             print("   Resumen totals correct.")
        else:
             print("ERROR: Resumen totals incorrect.")
    else:
        print("ERROR: Validation failed unexpected.")

    print("\n2. Testing validate_batch (Error Case - Zero Weight)...")
    original_weight = guias[1].peso_bruto
    guias[1].peso_bruto = Decimal("0.00")
    result_err = await service.validate_batch(guias)
    print("Result (Error expected):", result_err)
    if result_err["status"] == "ERROR":
        print("SUCCESS: Error detected correctly.")
    else:
        print("ERROR: Should have failed.")
    guias[1].peso_bruto = original_weight # Restore

    print("\n3. Testing generate_flat_file_content...")
    txt_content = service.generate_flat_file_content(guias)
    print("--- TXT CONTENT START ---")
    print(txt_content)
    print("--- TXT CONTENT END ---")
    
    if "FFM/8/LA2500" in txt_content and "FWB/99912345678" in txt_content:
        print("SUCCESS: TXT content looks correct (FFM Header + FWB Lines present).")
    else:
        print("ERROR: Missing expected FFM/FWB markers.")

    print("\n4. Testing generate_manifest_pdf...")
    pdf_buffer = await service.generate_manifest_pdf(guias)
    
    content = pdf_buffer.getvalue()
    if content.startswith(b"%PDF"):
         print(f"SUCCESS: Generated {len(content)} bytes of PDF data.")
    elif content.startswith(b"Error:"):
         print(f"WARNING: PDF Generation unavailable: {content}")
    else:
         print(f"ERROR: Output format unknown (Starts with: {content[:10]})")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_generation())
