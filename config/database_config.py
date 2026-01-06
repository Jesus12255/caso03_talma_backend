from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.config import settings

DATABASE_URL = settings.DATABASE_URL

from sqlalchemy.pool import NullPool

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "server_settings": {
            "jit": "off"
        },
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
