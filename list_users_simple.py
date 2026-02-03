import asyncio
from sqlalchemy import text
from config.database import async_session

async def list_users():
    async with async_session() as session:
        result = await session.execute(text("SELECT usuario_id, correo FROM usuario LIMIT 5"))
        users = result.fetchall()
        print("--- USERS ---")
        for u in users:
            print(f"ID: {u.usuario_id} | Email: {u.correo}")

if __name__ == "__main__":
    asyncio.run(list_users())
