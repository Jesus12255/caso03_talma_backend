import asyncio
import sys
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the project root to sys.path
sys.path.append(os.getcwd())

from config.database_config import DATABASE_URL

async def test():
    print("Testing DB connection...")
    try:
        engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"statement_cache_size": 0})
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Result: {result.fetchone()}")
        await engine.dispose()
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test())
