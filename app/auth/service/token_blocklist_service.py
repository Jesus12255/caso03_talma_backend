import redis.asyncio as redis
import logging
from config.config import settings

logger = logging.getLogger(__name__)

class TokenBlocklistService:
    @staticmethod
    def _get_redis_client():
        connection_kwargs = {
            "encoding": "utf-8",
            "decode_responses": True
        }
        
        if settings.REDIS_URL.startswith("rediss://"):
            connection_kwargs["ssl_cert_reqs"] = "none"

        return redis.from_url(settings.REDIS_URL, **connection_kwargs)

    @staticmethod
    async def add_to_blocklist(jti: str, expire_seconds: int):
        """
        Agrega un jti (JWT ID) a la lista de bloqueos en Redis.
        Expira automáticamente cuando expira la duración original del token,
        para no saturar la memoria de Redis con tokens que de todos modos ya habrían expirado.
        """
        try:
            if not jti or expire_seconds <= 0:
                return

            client = TokenBlocklistService._get_redis_client()
            # El valor no importa mucho, solo queremos saber si existe la key.
            await client.setex(f"blocklist:{jti}", expire_seconds, "revoked")
            await client.close()
            logger.info(f"Token (jti={jti}) añadido a la blocklist. Expira en {expire_seconds} segundos.")
        except Exception as e:
            logger.error(f"Error añadiendo a la blocklist en Redis: {e}")

    @staticmethod
    async def is_blocklisted(jti: str) -> bool:
        """
        Verifica si un jti ha sido revocado (existe en Redis).
        """
        if not jti:
            return False

        try:
            client = TokenBlocklistService._get_redis_client()
            exists = await client.exists(f"blocklist:{jti}")
            await client.close()
            return exists > 0
        except Exception as e:
            logger.error(f"Error verificando blocklist en Redis: {e}")
            # En caso de fallo de Redis, podríamos permitir o denegar por defecto (Fall-open o Fall-closed).
            # Para balances de seguridad/disponibilidad empresarial sin una caché de respaldo,
            # lo común es Fall-open (retornar False y loguear) a menos que sea una app de criticidad extrema.
            return False
