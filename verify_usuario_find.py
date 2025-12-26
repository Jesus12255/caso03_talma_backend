import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.security.repository.impl.usuario_repository_impl import UsuarioRepositoryImpl
from dto.usuario_dtos import UsuarioFiltroRequest
from config.database_config import DATABASE_URL

async def verify_find():
    print("Starting user find verification...")
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            repo = UsuarioRepositoryImpl(session)
            
            # Test 1: Find all (paginated)
            print("\nTest 1: Find all")
            req = UsuarioFiltroRequest(limit=5, start=0)
            users, count = await repo.find(req)
            print(f"Total count: {count}")
            print(f"Found {len(users)} users")
            if users:
                print(f"First user: {users[0].nombre_completo} - {users[0].rol}")

            # Test 2: Find by string in name (assuming some common letter)
            print("\nTest 2: Find by name 'a'")
            req_name = UsuarioFiltroRequest(nombre="a", limit=5)
            users_name, count_name = await repo.find(req_name)
            print(f"Total count: {count_name}")
            for u in users_name:
                print(f"   - {u.nombre_completo}")

            # Test 3: Find by rol code (if we found one in Test 1)
            if users:
                target_rol = users[0].rol_codigo
                if target_rol:
                    print(f"\nTest 3: Find by rol {target_rol}")
                    req_rol = UsuarioFiltroRequest(rolCodigo=target_rol, limit=5)
                    users_rol, count_rol = await repo.find(req_rol)
                    print(f"Total count: {count_rol}")

        await engine.dispose()
        print("\nVerification finished successfully.")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_find())
