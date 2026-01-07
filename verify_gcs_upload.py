import asyncio
import os
from dotenv import load_dotenv

# Force loading env from current dir before importing app logic
load_dotenv(".env")

from app.integration.service.impl.gcp_storage_service_impl import GcpStorageServiceImpl

async def main():
    print("--- Verifying GCP Storage Upload (Env Vars) ---")
    
    # Check Env
    project = os.getenv("GCP_PROJECT_ID")
    email = os.getenv("GCP_CLIENT_EMAIL")
    key = os.getenv("GCP_PRIVATE_KEY")
    bucket = os.getenv("GCS_BUCKET_NAME")
    
    print(f"Project: {project}")
    print(f"Email: {email}")
    print(f"Key Present: {'Yes' if key else 'No'}")
    print(f"Bucket: {bucket}")
    
    if not project or not email or not key or not bucket:
        print("ERROR: Missing GCP environment variables.")
    
    # We proceed anyway
    service = GcpStorageServiceImpl()
    
    filename = "test_upload_verify.txt"
    content = b"Hello GCP! This is a verification upload."
    content_type = "text/plain"
    
    try:
        print(f"Uploading {filename}...")
        url = await service.upload_file(filename, content, content_type)
        print(f"SUCCESS! File uploaded.")
        print(f"Public URL: {url}")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(main())
