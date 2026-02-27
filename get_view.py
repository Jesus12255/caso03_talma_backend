import asyncio
from sqlalchemy import text
from app.db.database import config

async def print_view():
    async for session in config.get_db():
        result = await session.execute(text(\"SELECT pg_get_viewdef('vw_perfil_riesgo', true);\"))
        print(result.scalar())
        break

asyncio.run(print_view())
