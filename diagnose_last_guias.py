
import asyncio
import sys
import os

# Ensure project root is in python path
sys.path.append(os.getcwd())

from config.database_config import AsyncSessionLocal
from app.core.domain.guia_aerea import GuiaAerea
from app.core.domain.manifiesto import Manifiesto
from sqlalchemy import select, desc

async def diagnose():
    async with AsyncSessionLocal() as session:
        print("Fetching last 5 modified GuiaAerea records...")
        stmt = select(GuiaAerea).order_by(desc(GuiaAerea.modificado)).limit(5)
        result = await session.execute(stmt)
        guias = result.scalars().all()

        print(f"{'ID':<36} | {'Numero':<15} | {'Estado':<10} | {'Vuelo':<10} | {'Fecha Vuelo':<20} | {'Manifiesto ID'}")
        print("-" * 120)
        for g in guias:
            vuelo = g.numero_vuelo if g.numero_vuelo else "None"
            fecha = str(g.fecha_vuelo) if g.fecha_vuelo else "None"
            manifiesto = str(g.manifiesto_id) if g.manifiesto_id else "None"
            print(f"{g.guia_aerea_id} | {g.numero:<15} | {g.estado_registro_codigo:<10} | {vuelo:<10} | {fecha:<20} | {manifiesto}")

if __name__ == "__main__":
    asyncio.run(diagnose())
