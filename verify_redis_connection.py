
import os
from dotenv import load_dotenv
import redis

# Force reload of .env
load_dotenv(override=True)

redis_url = os.getenv("REDIS_URL")
print(f"Testing connection to: {redis_url.split('@')[-1] if '@' in redis_url else 'LOCAL'}")

try:
    if redis_url.startswith("rediss://"):
        # SSL connection
        r = redis.from_url(redis_url, ssl_cert_reqs="none")
    else:
        r = redis.from_url(redis_url)
    
    response = r.ping()
    print(f"PING response: {response}")
    
    # Write a test key
    r.set("test_key", "Hello from Local to Vercel!")
    value = r.get("test_key")
    print(f"Read back value: {value.decode('utf-8')}")
    
except Exception as e:
    print(f"ERROR: {e}")
