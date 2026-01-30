from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.websockets.manager import manager
from config.config import settings
import redis.asyncio as redis
import asyncio
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantener conexion viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def redis_connector():
    """Conecta a Redis y escucha mensajes para hacer broadcast a WebSockets"""
    try:
        while True:
            try:
                connection_kwargs = {"socket_connect_timeout": 2}
                if settings.REDIS_URL.startswith("rediss://"):
                     connection_kwargs["ssl_cert_reqs"] = "none"

                redis_conn = redis.from_url(settings.REDIS_URL, **connection_kwargs)
                async with redis_conn.pubsub() as pubsub:
                    await pubsub.subscribe("document_updates")
                    logger.info(f"Conectado a Redis para WebSockets en {settings.REDIS_URL}")
                    
                    async for message in pubsub.listen():
                        if message["type"] == "message":
                            data = message["data"].decode("utf-8")
                            await manager.broadcast(data)
            except asyncio.CancelledError:
                logger.info("Redis connector task cancelled (inner).")
                return
            except Exception as e:
                logger.error(f"Error conexión Redis (Reintentando en 5s): {e}")
                await asyncio.sleep(5)
    except asyncio.CancelledError:
        logger.info("Redis connector task cancelled (outer).")
        return
