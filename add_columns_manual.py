import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load env vars
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def add_columns():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found.")
        return

    print(f"Connecting to DB...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        print("Adding column 'es_valido'...")
        try:
            await conn.execute(text("ALTER TABLE manifiesto ADD COLUMN es_valido BOOLEAN DEFAULT FALSE"))
            print(" - 'es_valido' added.")
        except Exception as e:
            print(f" - Error adding 'es_valido' (might exist): {e}")

        print("Adding column 'errores_validacion'...")
        try:
            await conn.execute(text("ALTER TABLE manifiesto ADD COLUMN errores_validacion TEXT"))
            print(" - 'errores_validacion' added.")
        except Exception as e:
             print(f" - Error adding 'errores_validacion' (might exist): {e}")

    await engine.dispose()
    print("Done.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_columns())
