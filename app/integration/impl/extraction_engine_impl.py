import json
import asyncio
import base64
import logging
from google import genai
from google.genai import types
from app.integration.extraction_engine import ExtractionEngine
from config.config import settings



logger = logging.getLogger(__name__)


key_len = len(settings.LLM_API_KEY) if settings.LLM_API_KEY else 0
masked_key = f"{settings.LLM_API_KEY[:3]}...{settings.LLM_API_KEY[-3:]}" if key_len > 6 else "SHORT_KEY"


class ExtractionEngineImpl(ExtractionEngine):

    async def extract_single_document(self, base64_data: str, mime_type: str, page_count: int, start_index: int) -> list[dict]:
        client = genai.Client(api_key=settings.LLM_API_KEY)
        
        is_pdf = mime_type == "application/pdf"
        is_text = mime_type == "text/plain"

        system_instructions = """Eres un experto en extracción de datos (OCR) y análisis de guías aéreas (Air Waybill).
Tu objetivo es extraer TODA la información del documento adjunto de forma estructurada.

REGLAS DE ORO:
1. Los 'intervinientes' deben seguir este orden ESTRICTO:
   - 1ro: Remitente (Shipper) con tipoCodigo: "TPIN001".
   - 2do: Consignatario (Consignee) con tipoCodigo: "TPIN002".
2. Usa camelCase ESTRICTO para los nombres de los campos.
3. Incluye una lista 'confianzas'.
4. Si el texto es MANUSCRITO, transcríbelo fielmente.
5. NO inventes datos. Si es ilegible, usa null.
6. Devuelve SIEMPRE una lista (array) JSON.
7. Genera objetos separados si detectas múltiples guías ("MASTER AWB NO") diferentes.

REGLAS ESPECÍFICAS DE NEGOCIO (IMPORTANTE):
8. **ORIGEN (origenCodigo):** Ubica la casilla "Airport of Departure". 
   - Si el texto es un nombre completo (ej. "PUDONG", "SHANGHAI"), **DEBES INFERIR Y DEVOLVER EL CÓDIGO IATA** de 3 letras (ej. "PVG", "SHA"). 
   - Prioriza el código IATA estándar sobre el nombre escrito.
   
9. **DESTINO (destinoCodigo):** Ubica la casilla "Airport of Destination" o el último código en la ruta ("Routing"). 
   - Convierte nombres de ciudades a códigos IATA (ej. "LIMA" -> "LIM").

10. **TRASBORDO (transbordo):** Analiza la sección "Routing and Destination".
    - Mira las columnas "To" (Hacia).
    - El primer código que aparece bajo "To" suele ser una escala si es diferente al destino final.
    - Ejemplo: Si la ruta dice "To: HND", "To: LIM", entonces "HND" es el trasbordo.
    - Devuelve el código IATA de la escala.

11. **NÚMERO DE GUÍA:** El "MASTER AWB No." es el número principal (ej. 006-26406726).
12. **INSTRUCCIONES:** El campo "Handling Information" corresponde a 'instruccionesEspeciales'.
13. **MERCANCÍA:** Si falta información explícita, infiere detalles de "Nature and Quantity of Goods".

VALIDACIÓN:
Si el documento NO es una Guía Aérea, devuelve: { "error": "DOCUMENTO_INVALIDO", "mensaje": "..." }.
"""

        few_shot_structure = """
Estructura esperada:
[
    {
        "intervinientes": [
            {
                "nombre": "MetalMecánica Andina SAC",
                "direccion": "Av. Los Talleres 789",
                "ciudad": "Callao",
                "paisCodigo": "PE",
                "telefono": "+51 987654321",
                "tipoDocumentoCodigo": "RUC",
                "numeroDocumento": "20432109876",
                "tipoCodigo": "TPIN001"
            },
            {
                "nombre": "Nordic Industrial Equipment AB",
                "direccion": "Västra Hamngatan 12",
                "ciudad": "Gothenburg",
                "paisCodigo": "SE",
                "telefono": "+46 317889900",
                "tipoDocumentoCodigo": "VAT_ID",
                "numeroDocumento": "SE55667788",
                "tipoCodigo": "TPIN002"
            }
        ],
        "numero": "145-55443322",
        "fechaEmision": "2025-10-02T14:25:00",
        "estadoGuiaCodigo": "REVISION_MANUAL",
        "origenCodigo": "LIM",
        "destinoCodigo": "GOT",
        "transbordo": "FRA",
        "aerolineaCodigo": "LH",
        "numeroVuelo": "LH9090",
        "fechaVuelo": "2025-10-04T01:55:00",
        "descripcionMercancia": "Componentes metálicos para maquinaria",
        "cantidadPiezas": 60,
        "pesoBruto": 5100.30,
        "pesoCobrado": 5050.00,
        "unidadPesoCodigo": "KG",
        "volumen": 26.75,
        "naturalezaCargaCodigo": "GENERAL",
        "valorDeclarado": 103500.00,
        "tipoFleteCodigo": "COBRAR",
        "tarifaFlete": 11240.00,
        "otrosCargos": 920.00,
        "monedaCodigo": "EUR",
        "totalFlete": 12160.00,
        "instruccionesEspeciales": "Asegurar correctamente la carga",
        "observaciones": "Algunos textos con baja nitidez",
        "confianzas": [
            { "nombreCampo": "numero", "valorExtraido": "145-55443322", "confidenceModelo": 0.93 },
            { "nombreCampo": "fechaEmision", "valorExtraido": "2025-10-02T14:25:00", "confidenceModelo": 0.92 },
            { "nombreCampo": "estadoGuiaCodigo", "valorExtraido": "REVISION_MANUAL", "confidenceModelo": 0.91 },
            { "nombreCampo": "origenCodigo", "valorExtraido": "LIM", "confidenceModelo": 0.94 },
            { "nombreCampo": "destinoCodigo", "valorExtraido": "GOT", "confidenceModelo": 0.93 },
            { "nombreCampo": "transbordo", "valorExtraido": "FRA", "confidenceModelo": 0.88 },
            { "nombreCampo": "aerolineaCodigo", "valorExtraido": "LH", "confidenceModelo": 0.95 },
            { "nombreCampo": "numeroVuelo", "valorExtraido": "LH9090", "confidenceModelo": 0.90 },
            { "nombreCampo": "fechaVuelo", "valorExtraido": "2025-10-04T01:55:00", "confidenceModelo": 0.92 },
            { "nombreCampo": "descripcionMercancia", "valorExtraido": "Componentes metálicos para maquinaria", "confidenceModelo": 0.89 },
            { "nombreCampo": "cantidadPiezas", "valorExtraido": "60", "confidenceModelo": 0.94 },
            { "nombreCampo": "pesoBruto", "valorExtraido": "5100.30", "confidenceModelo": 0.87 },
            { "nombreCampo": "pesoCobrado", "valorExtraido": "5050.00", "confidenceModelo": 0.86 },
            { "nombreCampo": "unidadPesoCodigo", "valorExtraido": "KG", "confidenceModelo": 0.96 },
            { "nombreCampo": "volumen", "valorExtraido": "26.75", "confidenceModelo": 0.88 },
            { "nombreCampo": "naturalezaCargaCodigo", "valorExtraido": "GENERAL", "confidenceModelo": 0.91 },
            { "nombreCampo": "valorDeclarado", "valorExtraido": "103500.00", "confidenceModelo": 0.92 },
            { "nombreCampo": "tipoFleteCodigo", "valorExtraido": "COBRAR", "confidenceModelo": 0.93 },
            { "nombreCampo": "tarifaFlete", "valorExtraido": "11240.00", "confidenceModelo": 0.90 },
            { "nombreCampo": "otrosCargos", "valorExtraido": "920.00", "confidenceModelo": 0.88 },
            { "nombreCampo": "monedaCodigo", "valorExtraido": "EUR", "confidenceModelo": 0.95 },
            { "nombreCampo": "totalFlete", "valorExtraido": "12160.00", "confidenceModelo": 0.92 },
            { "nombreCampo": "instruccionesEspeciales", "valorExtraido": "Asegurar correctamente la carga", "confidenceModelo": 0.89 },
            { "nombreCampo": "observaciones", "valorExtraido": "Algunos textos con baja nitidez", "confidenceModelo": 0.87 },

            { "nombreCampo": "remitente.nombre", "valorExtraido": "MetalMecánica Andina SAC", "confidenceModelo": 0.94 },
            { "nombreCampo": "remitente.direccion", "valorExtraido": "Av. Los Talleres 789", "confidenceModelo": 0.90 },
            { "nombreCampo": "remitente.ciudad", "valorExtraido": "Callao", "confidenceModelo": 0.92 },
            { "nombreCampo": "remitente.paisCodigo", "valorExtraido": "PE", "confidenceModelo": 0.96 },
            { "nombreCampo": "remitente.numeroDocumento", "valorExtraido": "20432109876", "confidenceModelo": 0.95 },
            { "nombreCampo": "remitente.telefono", "valorExtraido": "+51 987654321", "confidenceModelo": 0.89 },

            { "nombreCampo": "consignatario.nombre", "valorExtraido": "Nordic Industrial Equipment AB", "confidenceModelo": 0.94 },
            { "nombreCampo": "consignatario.direccion", "valorExtraido": "Västra Hamngatan 12", "confidenceModelo": 0.90 },
            { "nombreCampo": "consignatario.ciudad", "valorExtraido": "Gothenburg", "confidenceModelo": 0.92 },
            { "nombreCampo": "consignatario.paisCodigo", "valorExtraido": "SE", "confidenceModelo": 0.96 },
            { "nombreCampo": "consignatario.telefono", "valorExtraido": "+46 317889900", "confidenceModelo": 0.88 },
            { "nombreCampo": "consignatario.numeroDocumento", "valorExtraido": "SE55667788", "confidenceModelo": 0.91 }
        ]
    }
]"""

        prompt_text = ""
        contents = []

        if is_text:
            prompt_text = f"""{system_instructions}

Analiza este contenido de TEXTO (Excel/CSV/Word/Documento).
Responde con una lista.

{few_shot_structure}

Formato requerido:
[
  {{...}},
  ...
]"""
            try:
                decoded_text = base64.b64decode(base64_data).decode('utf-8')
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=prompt_text),
                            types.Part(text=decoded_text)
                        ]
                    )
                ]
            except:
                 contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=prompt_text),
                            types.Part(text=base64_data)
                        ]
                    )
                ]

        elif is_pdf:
            prompt_text = f"""{system_instructions}

Analiza este documento PDF por completo ({page_count} páginas).
Identifica todas las Guías Aéreas distintas presentes.

REGLA DE FUSIÓN DE PÁGINAS:
- Si una sola Guía Aérea continúa en varias páginas (ej. página 1 y 2), COMBINA toda la información en un ÚNICO objeto JSON.
- Si hay múltiples guías distintas (ej. una en pág 1, otra en pág 2), devuelve OBJETOS SEPARADOS.
- Devuelve una lista con un objeto por cada Guía Aérea lógica encontrada.

{few_shot_structure}

Formato requerido:
[
  {{...}},
  ...
]"""
            pdf_bytes = base64.b64decode(base64_data)
            contents = [
                types.Content(
                    role="user",
                    parts=[
                         types.Part(text=prompt_text),
                         types.Part(inline_data=types.Blob(data=pdf_bytes, mime_type=mime_type))
                    ]
                )
            ]
        else:
            # Images
            prompt_text = f"""{system_instructions}

Analiza esta IMAGEN de una Guía Aérea. Puede contener texto MANUSCRITO.
Es fundamental extraer todos los datos y la lista de intervinientes.

{few_shot_structure}

Formato requerido:
[
  {{...}}
]"""
            img_bytes = base64.b64decode(base64_data)
            contents = [
                types.Content(
                    role="user",
                    parts=[
                         types.Part(text=prompt_text),
                         types.Part(inline_data=types.Blob(data=img_bytes, mime_type=mime_type))
                    ]
                )
            ]

        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"AI Call attempt {attempt+1} for index {start_index} (Mime: {mime_type}, Model: {settings.LLM_MODEL_NAME})")
                
                response = await client.aio.models.generate_content(
                    model=settings.LLM_MODEL_NAME,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                
                if response.text:
                    text = response.text.strip()
                    logger.debug(f"AI Raw Response for {start_index}: {text[:300]}...")
                    
                    if text.startswith("```"):
                        lines = text.splitlines()
                        if lines[0].startswith("```"): lines = lines[1:]
                        if lines[-1].startswith("```"): lines = lines[:-1]
                        text = "\n".join(lines).strip()
                    
                    try:
                        result_data = json.loads(text)
                    except json.JSONDecodeError:
                        logger.error(f"JSON ERROR for index {start_index}: {text}")
                        return [{"document_index": start_index, "error": "LLM returned invalid JSON"}]

                    extracted_list = []
                    if isinstance(result_data, list):
                        extracted_list = result_data
                    elif isinstance(result_data, dict):
                        for key in ["documents", "results", "pages", "data"]:
                            if key in result_data and isinstance(result_data[key], list):
                                extracted_list = result_data[key]
                                break
                        if not extracted_list:
                            extracted_list = [result_data]
                    
                    for item in extracted_list:
                        if not isinstance(item, dict): continue
                        if "document_index" not in item: item["document_index"] = start_index
                        if "document_name" not in item: item["document_name"] = f"Documento {start_index}"
                        
                        # Fix: Si la IA devuelve la estructura plana, la respetamos
                        # No envolvemos forzosamente en 'fields'
                        pass
                    
                    return extracted_list
                else:
                    return [{"document_index": start_index, "error": "Empty AI response"}]

            except Exception as e:
                logger.error(f"AI Error for index {start_index}: {e}", exc_info=True)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return [{"document_index": start_index, "error": str(e)}]
        
        return [{"document_index": start_index, "error": "Max retries exceeded"}]