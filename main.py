from app.core.domain.document import Base
from config.app_logging import setup_logging
from config.router_doc_config import app
from config.cors_config import setup_cors
from config.router_config import setup_routes
from config.database_config import engine
from sqlalchemy.ext.asyncio import AsyncSession

setup_logging()
setup_cors(app)
setup_routes(app)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_models()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
