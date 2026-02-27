import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.repository.impl.perfil_riesgo_repository_impl import PerfilRiesgoRepositoryImpl

engine = create_async_engine('postgresql+asyncpg://postgres.jinyomztyfhqrjwglyyb:Tivit2025..@aws-1-sa-east-1.pooler.supabase.com:6543/postgres')
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    async with AsyncSessionLocal() as session:
        repo = PerfilRiesgoRepositoryImpl(session)
        res = await repo.find_dispersion_by_perfil('c484dd0b-ce59-46c8-bac2-60f8f19f97a7')
        print(res)

if __name__ == "__main__":
    asyncio.run(main())
