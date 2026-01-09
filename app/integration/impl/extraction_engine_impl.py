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
3. Incluye una lista 'confianzas'. CRITERIO: Si el texto es claro, confianza >= 0.95. Solo si es borroso/ambiguo (si puedes llegara inferir 2 textos o mas a partir del mismo texto) baja de 0.95.
4. Si el texto es MANUSCRITO, transcríbelo fielmente.
5. NO inventes datos. Si es ilegible, usa null.
6. Devuelve SIEMPRE una lista (array) JSON.
7. Genera objetos separados si detectas múltiples guías ("MASTER AWB NO") diferentes.

ESTRATEGIA DE INFERENCIA PARA DATOS SIN ETIQUETAS (CRÍTICO):
A menudo, las guías no tienen títulos de campo ("Shipper", "Consignee", "Weight"), solo valores en posiciones estándar.
Usa tu conocimiento del formato IATA Air Waybill para inferir qué es cada dato:
- **Aeropuertos**: Si ves códigos de 3 letras (ej. LIM, MIA, MAD) aislados, el primero/izquierdo suele ser ORIGEN y el segundo/derecho DESTINO.
- **Participantes**:
    - El bloque de texto en la esquina superior izquierda es siempre el REMITENTE (Shipper).
    - El bloque de texto justo debajo del remitente es el CONSIGNATARIO (Consignee).
- **Valores Numéricos**:
    - Enteros pequeños (1-1000) a la izquierda de un peso suelen ser "cantidadPiezas".
    - Números con decimales seguidos de "K", "KG", "L", "LB" son "pesoBruto".
    - Valores monetarios (decimales) en columnas alineadas a la derecha suelen ser "totalFlete" o cargos.
- **Códigos**: 
    - "PP" o "CC" aislados indican "tipoFleteCodigo" (Prepaid/Collect).
    - Códigos de 3 letras bajo columnas de "Routing" son Escalas/Trasbordos.

REGLAS ESPECÍFICAS DE NEGOCIO (IMPORTANTE):
8. **ORIGEN (origenCodigo):** Busca "Airport of Departure" o el primer código IATA (3 letras) lógico.
   - Si es nombre completo (ej. "SHANGHAI"), **DEBES INFERIR EL CÓDIGO IATA** (ej. "SHA").
   
9. **DESTINO (destinoCodigo):** Busca "Airport of Destination" o el código IATA final.
   - Convierte nombres de ciudades a códigos IATA (ej. "LIMA" -> "LIM").

10. **TRASBORDO (transbordo):** Analiza ruta ("Routing").
    - Primer código IATA bajo "To" diferente al destino final.

11. **NÚMERO DE GUÍA:** Busca formato XXX-XXXXXXXX (ej. 006-26406726) en encabezados.
12. **INSTRUCCIONES:** "Handling Information" o texto libre con instrucciones.
13. **MERCANCÍA:** "Nature and Quantity of Goods" o descripción principal de la carga.
14. **INFERENCIA DE FECHA DE VUELO (LÓGICA TEMPORAL):**
    - **Paso 1 (Referencia):** Busca la fecha de firma/ejecución (usualmente abajo a la derecha, "Executed on"). Ej: "27-Dec-24".
    - **Paso 2 (Dato):** Mira "Requested Flight/Date". Si dice algo como "DL188/06", el número después de la barra ("06") es el DÍA.
    - **Paso 3 (Cálculo):**
        - Si el DÍA de vuelo (06) es MENOR que el DÍA de firma (27), significa que el vuelo es el MES SIGUIENTE. (Ej: Si firma Dic 27 y vuelo es día 06 -> Es 06 de Enero).
        - Si el DÍA de vuelo es MAYOR, es el mismo mes.
    - **Paso 4 (Salida):** Extrae SOLO la fecha del PRIMER vuelo en formato ISO (YYYY-MM-DD) en el campo "fechaVuelo". Ignora segundos vuelos.

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