import asyncio
import os
import sys

# Asegurar que el directorio actual esté en el path para importar configuraciones
sys.path.append(os.getcwd())

from sqlalchemy import text
from config.database_config import AsyncSessionLocal

async def fix_schema():
    print("Conectando a la base de datos...")
    async with AsyncSessionLocal() as session:
        try:
            print("Ejecutando: ALTER TABLE audit ALTER COLUMN usuario_id DROP NOT NULL")
            await session.execute(text("ALTER TABLE audit ALTER COLUMN usuario_id DROP NOT NULL"))
            await session.commit()
            print("¡Éxito! La columna usuario_id de la tabla audit ahora permite valores NULL.")
            print("Esto permitirá registrar auditorías generadas por el sistema (Celery) sin errores.")
        except Exception as e:
            print(f"Error al ejecutar el cambio: {e}")
            # Si el error es que la columna ya es nullable o la tabla no existe, no es grave, pero bueno saberlo.

if __name__ == "__main__":
    try:
        asyncio.run(fix_schema())
    except Exception as e:
        print(f"Error fatal al correr el script: {e}")
