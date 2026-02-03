from typing import List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Mapea user_id -> Lista de WebSockets (un usuario puede tener varias pestañas abiertas)
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for User {user_id}. Total: {len(self.active_connections.get(user_id, []))}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for User {user_id}")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending personal message to {user_id}: {e}")

    async def broadcast(self, message: str):
        # Broadcast global (opcional, si se necesita)
        for user_sockets in self.active_connections.values():
            for connection in user_sockets:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()
