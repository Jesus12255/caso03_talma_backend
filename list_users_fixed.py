import sys
import os
import asyncio
from sqlalchemy import text

# Add current CWD to sys.path
sys.path.append(os.getcwd())

from config.database import async_session

async def list_users():
    async with async_session() as session:
        result = await session.execute(text("SELECT usuario_id, correo FROM usuario LIMIT 1"))
        user = result.fetchone()
        if user:
            print(f"USER_ID:{user.usuario_id}")
            print(f"EMAIL:{user.correo}")
        else:
            print("NO_USERS_FOUND")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(list_users())
