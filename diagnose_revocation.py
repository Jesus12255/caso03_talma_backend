import asyncio
import sys
import os

# Añadir el path del proyecto para poder importar app
sys.path.append(os.getcwd())

from app.auth.service.token_blocklist_service import TokenBlocklistService
from jose import jwt
from config.config import settings
from datetime import datetime, timedelta
import uuid

async def diagnose():
    print("--- Diagnostic Starting ---")
    
    # Test 1: Generate a JTI and add to blocklist
    test_jti = f"test-jti-{uuid.uuid4()}"
    print(f"Testing with JTI: {test_jti}")
    
    is_blocked_init = await TokenBlocklistService.is_blocklisted(test_jti)
    print(f"Initially blocklisted? {is_blocked_init}")
    
    print("Adding to blocklist for 60 seconds...")
    await TokenBlocklistService.add_to_blocklist(test_jti, 60)
    
    is_blocked_after = await TokenBlocklistService.is_blocklisted(test_jti)
    print(f"Blocklisted after adding? {is_blocked_after}")
    
    if is_blocked_after == True:
        print("SUCCESS: Redis blocklist logic is working correctly.")
    else:
        print("FAILURE: Redis blocklist logic failed. Check Redis connection/URL.")

if __name__ == "__main__":
    asyncio.run(diagnose())
