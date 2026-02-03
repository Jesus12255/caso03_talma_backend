from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websockets.manager import manager
from config.config import settings
import redis.asyncio as redis
import asyncio
from jose import jwt
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    user_id = None
    logger.info(f"WS Connection Attempt. Token provided: {bool(token)}")
    if token:
        try:
            logger.info("Decoding WS Token...")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("usuarioId")
            logger.info(f"WS Token Decoded. UserID: {user_id}")
        except Exception as e:
            logger.error(f"Token de WebSocket inválido: {e}")
    
    if not user_id:
        logger.warning("WS Connection Rejected: No valid user_id found")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # Mantener conexion viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

async def redis_connector():
    """Conecta a Redis y escucha mensajes PRIVADOS para hacer broadcast a sockets específicos"""
    try:
        while True:
            try:
                connection_kwargs = {"socket_connect_timeout": 2}
                if settings.REDIS_URL.startswith("rediss://"):
                     connection_kwargs["ssl_cert_reqs"] = "none"

                redis_conn = redis.from_url(settings.REDIS_URL, **connection_kwargs)
                async with redis_conn.pubsub() as pubsub:
                    # Suscribirse a patrones de usuario: user:*:notifications
                    pattern = "user:*:notifications"
                    await pubsub.psubscribe(pattern)
                    logger.info(f"Conectado a Redis PubSub (Pattern: {pattern}) en {settings.REDIS_URL}")
                    
                    async for message in pubsub.listen():
                        if message["type"] == "pmessage":
                            # message structure: {'type': 'pmessage', 'pattern': b'...', 'channel': b'user:123:notifications', 'data': b'{...}'}
                            channel = message["channel"].decode("utf-8") # e.g., "user:uuid:notifications"
                            data = message["data"].decode("utf-8")
                            
                            # Extraer ID del canal
                            # channel.split(":") -> ["user", "uuid-bla-bla", "notifications"]
                            parts = channel.split(":")
                            if len(parts) == 3:
                                target_user_id = parts[1]
                                await manager.send_personal_message(data, target_user_id)
            except asyncio.CancelledError:
                logger.info("Redis connector task cancelled (inner).")
                return
            except Exception as e:
                logger.error(f"Error conexión Redis (Reintentando en 5s): {e}")
                await asyncio.sleep(5)
    except asyncio.CancelledError:
        logger.info("Redis connector task cancelled (outer).")
        return
