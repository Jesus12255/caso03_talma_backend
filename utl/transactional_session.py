from contextlib import asynccontextmanager
from config.database_config import AsyncSessionLocal

class TransactionalSession:
    @staticmethod
    @asynccontextmanager
    async def create_session():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except BaseException:
                await session.rollback()
                raise
            finally:
                await session.close()
