import asyncio
import logging
from typing import AsyncGenerator
import httpx
from google.cloud import storage
from app.integration.service.storage_service import StorageService
from config.config import settings

logger = logging.getLogger(__name__)

from google.oauth2 import service_account

from google.auth.transport.requests import Request

class GcpStorageServiceImpl(StorageService):
    
    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        
        info = {
            "type": "service_account",
            "project_id": settings.GCP_PROJECT_ID,
            "private_key_id": "unknown", 
            "private_key": settings.GCP_PRIVATE_KEY.replace('\\n', '\n'),
            "client_email": settings.GCP_CLIENT_EMAIL,
            "client_id": "unknown",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        creds = service_account.Credentials.from_service_account_info(info)
        # Alcance necesario para lectura/escritura
        self.creds = creds.with_scopes([
            "https://www.googleapis.com/auth/devstorage.read_write"
        ])
        self.client = storage.Client(credentials=self.creds, project=settings.GCP_PROJECT_ID)
        
    async def upload_file(self, filename: str, content: bytes, content_type: str) -> str:
        try:
            loop = asyncio.get_running_loop()
            url = await loop.run_in_executor(
                None, 
                self._upload_sync, 
                filename, 
                content, 
                content_type
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to GCS: {e}")
            raise e

    def _upload_sync(self, filename: str, content: bytes, content_type: str) -> str:
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(filename)
        
        blob.upload_from_string(
            content,
            content_type=content_type
        )
        
        return blob.public_url
        
    def _get_fresh_token_sync(self) -> str:
        if not self.creds.valid:
            self.creds.refresh(Request())
        return self.creds.token

    async def download_file_stream(self, url: str) -> AsyncGenerator[bytes, None]:
        try:
            loop = asyncio.get_running_loop()
            token = await loop.run_in_executor(None, self._get_fresh_token_sync)
        except Exception as e:
            logger.error(f"Error obteniendo token de acceso GCP: {e}")
            raise e

        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream("GET", url, headers=headers) as response:
                    if response.status_code != 200:
                        raise Exception(f"Error al descargar desde GCP: {response.status_code} - {response.reason_phrase}")

                    async for chunk in response.aiter_bytes():
                        yield chunk
            except Exception as e:
                logger.error(f"Error en download_file_stream: {e}")
                raise e
