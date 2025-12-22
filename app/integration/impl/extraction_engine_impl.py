import json

import httpx
from app.integration.extraction_engine import ExtractionEngine
from config.config import settings

class ExtractionEngineImpl(ExtractionEngine):

    async def extract_stream(self, base64_images: list[str]):
        url = f"{settings.LLM_BASE_URL}/generate"

        payload = {
            "model": settings.LLM_MODEL_NAME,
            "prompt": """Analiza las imágenes proporcionadas. Tu tarea PRINCIPAL es EXTRAER DATOS y CAMPOS ESPECÍFICOS de cada imagen en este formato JSON estructurado:
{
  "documents": [
    {
      "document_name": "nameDocument example",
      "fields": {
        "clave": "valor_exacto_extraido"
      }
    }
  ]
}
Genera un ÚNICO objeto JSON con la clave raíz "documents". 
El objeto "fields" es OBLIGATORIO y debe contener todos los datos clave detectados (fechas, nombres, montos, identificadores, tablas, etc.) como pares clave-valor.
Prioriza la fidelidad de los datos extraídos.
NO respondas con texto plano, solo JSON válido.
NO aplanes la estructura.
IMPORTANTE: dame un objeto dentro de documents por cada imagen proporcionada.
""",
            "images": base64_images,
            "stream": True,
            "format": "json"
        }

        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                async for chunk in response.aiter_text():
                    yield chunk  # pasa el token a AnalyzeServiceImpl