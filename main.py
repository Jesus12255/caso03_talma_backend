
from app.core.domain.base_model import Base
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
    
    # Iniciar listener de Redis para WebSockets
    import asyncio
    from core.realtime.websocket import redis_connector
    
    # Keep a strong reference to the task to avoid it being garbage collected
    if not hasattr(app.state, "background_tasks"):
        app.state.background_tasks = set()
    
    task = asyncio.create_task(redis_connector())
    app.state.background_tasks.add(task)
    task.add_done_callback(app.state.background_tasks.discard)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
