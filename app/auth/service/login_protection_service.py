import redis.asyncio as redis
import logging
from datetime import datetime, timezone
from config.config import settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class LoginProtectionService:
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION_SECONDS = 900  # 15 minutes

    @staticmethod
    def _get_redis_client():
        connection_kwargs = {
            "encoding": "utf-8",
            "decode_responses": True
        }
        if settings.REDIS_URL.startswith("rediss://"):
            import ssl
            connection_kwargs["ssl_cert_reqs"] = ssl.CERT_REQUIRED
        return redis.from_url(settings.REDIS_URL, **connection_kwargs)

    @staticmethod
    async def check_lockout(email: str, ip: str):
        """
        Checks if a user/IP combination is currently locked out.
        Raises 429 Too Many Requests if locked.
        """
        client = LoginProtectionService._get_redis_client()
        
        # Keys for tracking
        user_key = f"login_attempts:user:{email}"
        ip_key = f"login_attempts:ip:{ip}"
        
        # Check if already locked out (we use a special key for lockout)
        user_locked = await client.get(f"lockout:user:{email}")
        ip_locked = await client.get(f"lockout:ip:{ip}")
        
        if user_locked or ip_locked:
            await client.close()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please try again in 15 minutes."
            )
            
        await client.close()

    @staticmethod
    async def register_failure(email: str, ip: str):
        """
        Registers a failed login attempt.
        Increment counters and sets lockout if threshold is reached.
        """
        client = LoginProtectionService._get_redis_client()
        user_key = f"login_attempts:user:{email}"
        ip_key = f"login_attempts:ip:{ip}"
        
        # Increment attempts
        user_attempts = await client.incr(user_key)
        ip_attempts = await client.incr(ip_key)
        
        # Set expiry for the counters if first attempt
        if user_attempts == 1:
            await client.expire(user_key, LoginProtectionService.LOCKOUT_DURATION_SECONDS)
        if ip_attempts == 1:
            await client.expire(ip_key, LoginProtectionService.LOCKOUT_DURATION_SECONDS)
            
        # Check for lockout
        if user_attempts >= LoginProtectionService.MAX_ATTEMPTS:
            await client.setex(f"lockout:user:{email}", LoginProtectionService.LOCKOUT_DURATION_SECONDS, "locked")
            logger.warning(f"User {email} locked out due to multiple failed attempts.")
            
        if ip_attempts >= LoginProtectionService.MAX_ATTEMPTS:
            await client.setex(f"lockout:ip:{ip}", LoginProtectionService.LOCKOUT_DURATION_SECONDS, "locked")
            logger.warning(f"IP {ip} locked out due to multiple failed attempts.")
            
        await client.close()

    @staticmethod
    async def reset_attempts(email: str, ip: str):
        """
        Resets failure counters after a successful login.
        """
        client = LoginProtectionService._get_redis_client()
        await client.delete(f"login_attempts:user:{email}")
        await client.delete(f"login_attempts:ip:{ip}")
        # Note: We don't delete lockout keys here because a successful login 
        # normally shouldn't happen if locked, but just in case:
        await client.delete(f"lockout:user:{email}")
        await client.delete(f"lockout:ip:{ip}")
        await client.close()
