
import redis.asyncio as redis
import json
import logging
from config.config import settings
from utl.date_util import DateUtil

logger = logging.getLogger(__name__)

async def publish_document_update(type: str, message: str, doc_id: str = None):
    try:
        connection_kwargs = {
            "encoding": "utf-8",
            "decode_responses": True
        }
        
        if settings.REDIS_URL.startswith("rediss://"):
            connection_kwargs["ssl_cert_reqs"] = "none"

        r = redis.from_url(settings.REDIS_URL, **connection_kwargs)
        
        payload = {
            "type": type,
            "message": message,
            "documentId": str(doc_id) if doc_id else None,
            "timestamp": DateUtil.get_current_local_datetime().isoformat()
        }
        
        logger.info(f"Publishing Redis Update: {json.dumps(payload)}")
        
        await r.publish("document_updates", json.dumps(payload))
        await r.close()
    except Exception as e:
        logger.error(f"Error publishing to Redis: {e}")

async def publish_user_notification(user_id: str, type: str, message: str = "", doc_id: str = None, title: str = None, severity: str = "INFO", is_persistent: bool = False, notification_id: str = None):
    """Publica una notificación privada para un usuario específico"""
    try:
        connection_kwargs = {
            "encoding": "utf-8",
            "decode_responses": True
        }
        
        if settings.REDIS_URL.startswith("rediss://"):
            connection_kwargs["ssl_cert_reqs"] = "none"

        r = redis.from_url(settings.REDIS_URL, **connection_kwargs)
        
        payload = {
            "type": type,
            "title": title or "Notificación",
            "message": message,
            "documentId": str(doc_id) if doc_id else None,
            "severity": severity,
            "timestamp": DateUtil.get_current_local_datetime().isoformat(),
            "isPersistent": is_persistent,
            "notificationId": str(notification_id) if notification_id else None
        }
        
        # Canal específico del usuario: user:UUID:notifications
        channel = f"user:{user_id}:notifications"
        logger.info(f"Publishing User Notification to {channel}: {json.dumps(payload)}")
        
        await r.publish(channel, json.dumps(payload))
        await r.close()
    except Exception as e:
        logger.error(f"Error publishing user notification to Redis: {e}")
