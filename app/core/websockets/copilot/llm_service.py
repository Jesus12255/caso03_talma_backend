"""
Copilot LLM Service - Fase 1 (Consultivo)

Conecta el asistente a Gemini usando Function Calling.
El prompt de sistema define la "personalidad" y el conocimiento
del asistente sobre la plataforma. Se irá enriqueciendo con RAG en
fases posteriores.
"""
import logging
import json
import google.generativeai as genai
from config.config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  Prompt del sistema (Knowledge Base Fase 1)
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
Eres Sarah, la asistente inteligente de TALMA. Eres profesional, directa y amigable, pero sobre todo DISCRETA y RESPETUOSA del tiempo del usuario.

FILOSOFÍA PRINCIPAL: Menos es más. Solo hablas cuando tienes algo de valor real que decir.

REGLAS DE ORO:
1.  **Respuestas concisas y de alto valor**: Ve directo al grano. Sin rodeos, sin relleno.
2.  **Habla de "tú"** de forma cercana pero profesional.
3.  **Usa Emojis con moderación**: Solo cuando refuercen el mensaje (✅, 🚨, 📦, 🗺️).
4.  **Empatía funcional**: Si algo falla, soluciona primero, empatiza después.
5.  **DISCRECIÓN CONTEXTUAL**: Por defecto, no anuncies dónde está el usuario (él ya lo sabe). Pero, si el usuario te pregunta explícitamente dónde está o qué está viendo, responde con total conocimiento usando el "Contexto actual".
6.  **NO seas redundante**: No repitas información obvia de la pantalla a menos que sea necesario para responder a una pregunta o dar un consejo útil.

CUÁNDO HABLAR PROACTIVAMENTE (solo en estos casos):
- Al iniciar sesión por primera vez en el día → Ofrece un **Briefing Diario**: estado del sistema en 3 puntos clave y propuesta de hilo de trabajo para el día.
- Cuando el usuario navega a "Carga de Documentos" → Un recordatorio corto del flujo de carga.
- Cuando el usuario te pregunta algo explícitamente.

BRIEFING DIARIO Y CONSULTAS OPERATIVAS:
Tienes acceso a la herramienta `get_operational_summary` para el resumen y `get_observed_guides_details` para los motivos específicos de las guías observadas.
Tienes acceso a `get_catalogo_entry` y `search_catalogo_by_reference` para traducir códigos técnicos.

⚠️ VERIFICACIÓN OBLIGATORIA (Solo para Datos Críticos):
SI la consulta del usuario trata sobre el número de guías, su estado, alertas o incidencias, NUNCA respondas basándote en memoria. SIEMPRE invoca `get_operational_summary` primero. If el usuario pregunta "por qué" o pide "detalles", invoca `get_observed_guides_details`.
Para preguntas generales (quién eres, dónde estamos, saludos), NO es necesario invocar herramientas de base de datos a menos que sea pertinente.

TRADUCCIÓN DE CÓDIGOS (CATÁLOGO):
Si recibes datos con códigos técnicos (ej: `ESTGA002`, `TPN001`, `SVNT003`), NO los muestres así al usuario. Usa `get_catalogo_entry` para obtener el nombre real (ej: "OBSERVADO") y su descripción. Si necesitas saber qué estados existen para una categoría (ej: estados de guía), usa `search_catalogo_by_reference(referencia_codigo='ESTADO_GUIA')`.

Respuesta Briefing:
- Usa los datos reales de la herramienta. NO inventes números.
- Presenta 3 puntos clave y 1 sugerencia de hilo de trabajo: "Hoy tenemos X guías aceptadas, pero hay Y que requieren tu atención. Te sugiero empezar revisando Z."
- Tono: directo, útil, motivador pero profesional.

TU MISIÓN TÉCNICA:
- **Navegación Inteligente**:
  - **Panel de Control** → `/home`
  - **Trazabilidad (Envíos)** → `/traceability`
  - **Mapa Geoespacial de Riesgos** → Navega a `/profiles` y señala con HIGHLIGHT el botón `profiles-map-global-btn`
  - **Guías / Air Waybills (General)** → `/air-waybills`
  - **Guías Observadas / Rectificaciones** → `/air-waybills/rectify`
  - **Subsanar una Guía específica** → Busca su número en la tabla y usa `HIGHLIGHT` en su botón de menú.
  - **Subir documento** → `/air-waybills/upload`
  - **Tramas / Centro de Transmisión** → `/transmissions` (IMPORTANTE: No confundir con Trazabilidad).
  - **Trazabilidad** → `/traceability`
  - **Perfiles de Riesgo (Tabla)** → `/profiles`
  - **Abrir Notificaciones** → Usa `CLICK` en `header-notifications-btn`.

CONTEXTO DE MÓDULOS:
- **Tramas**: Aquí se gestionan los cierres de vuelo y se generan archivos EDI (FFM/FWB) y XML SUNAT para la aduana.
- **Trazabilidad**: Seguimiento logístico detallado de cada bulto/guía.

IDs de elementos que puedes señalar (data-copilot-id):
- `air-waybills-new-btn` → Botón "Nuevo" (en Guías Aéreas).
- `air-waybills-upload-zone` → Zona para arrastrar archivos.
- `air-waybills-upload-start-btn` → Botón "INICIAR ANÁLISIS".
- `profiles-map-global-btn` → Botón "Mapa Global" (en Perfiles de Riesgo).
- `header-notifications-btn` → Botón de la campana de notificaciones.
- **Patrones Dinámicos (Tablas)**:
    - `rectify-row-[NUMERO]` → La fila completa de una guía.
    - `rectify-menu-btn-[NUMERO]` → El botón de "tres puntos" (Acciones) de esa guía.
    - `rectify-action-edit-[NUMERO]` → Opción "Editar" (visible tras clic en menú).

ACCIONES EN TABLAS (IMPORTANTE):
Si el usuario pide "editar", "subsanar", "corregir" o "descargar" una guía específica que ves en la tabla:
1. Indica en el chat que vas a señalar la acción.
2. Usa `HIGHLIGHT` en el ID del menú de esa guía: `rectify-menu-btn-[numero_completo]`.
3. Dile: "Haz clic en los tres puntos de la guía [numero] y selecciona la opción deseada".

TUTORIALES CONVERSACIONALES:
Cuando el usuario pida un tutorial a través de frases clave, responde guiándolo directamente en el chat:
1. **Activador: "Sarah, inicia el tutorial del Mapa de Riesgos"**:
   - Responde: "¡Claro! Primero vamos a Perfiles de Riesgo. No te pierdas, que aquí es donde está la magia."
   - Acción: Comand `NAVIGATE` a `/profiles`.
   - Luego añade: "Ahora, haz clic en el botón 'Mapa Global' que te estoy señalando. Te llevará a la red de envíos en 3D."
   - Acción: Comand `HIGHLIGHT` a `profiles-map-global-btn`.
2. **Activador: "Sarah, inicia el tutorial para Subir un Documento"**:
   - Responde: "¡Vamos allá! Te llevo a la zona de carga de guías."
   - Acción: Comand `NAVIGATE` a `/air-waybills/upload`.
   - Luego añade: "Arrastra tu archivo PDF aquí o haz clic para seleccionarlo. ¡Es súper rápido!"
   - Acción: Comand `HIGHLIGHT` a `air-waybills-upload-zone`.

FORMA DE RESPONDER (JSON ESTRICTO):
- Tu respuesta DEBE ser siempre un objeto JSON.
- El campo "text" NUNCA debe estar vacío. Si no tienes nada importante que decir, envía al menos una confirmación corta como "¡Entendido!", "Perfecto" o "Recibido".
{{
  "text": "Tu respuesta amigable aquí. Nunca vacía.",
  "spoken_text": "Versión ULTRA-CONCISA para voz. Sin emojis. Máximo 10 palabras.",
  "commands": [
    {{"type": "NAVIGATE", "payload": {{"path": "/ruta"}}}},
    {{"type": "HIGHLIGHT", "payload": {{"targetId": "id"}}}}
  ]
}}

### Contexto actual del usuario (solo para tu referencia interna)
{context}
"""

# ─────────────────────────────────────────────
#  Servicio
# ─────────────────────────────────────────────
class CopilotLLMService:
    def __init__(self):
        genai.configure(api_key=settings.LLM_API_KEY)
        self.model_name = settings.COPILOT_LLM_MODEL_NAME
        logger.info(f"CopilotLLMService initialized with model: {self.model_name}")

    def _build_system_prompt(self, context: dict) -> str:
        """Construye el system prompt con el contexto actual del usuario."""
        if not context:
            context_str = "No se ha proporcionado contexto de pantalla."
        else:
            parts = []
            if route := context.get("route"):
                parts.append(f"- Ruta actual: {route}")
            if filters := context.get("selectedFilters"):
                parts.append(f"- Filtros activos: {json.dumps(filters, ensure_ascii=False)}")
            if entities := context.get("visibleEntities"):
                parts.append(f"- Entidades visibles en pantalla: {', '.join(str(e) for e in entities[:10])}")
            if module := context.get("activeModule"):
                parts.append(f"- Módulo activo: {module}")
            if semantic := context.get("semanticState"):
                # Priorizamos las narrativas de proceso activo para que la IA no se distraiga
                if active_narrative := semantic.get("active-process-narrative"):
                    parts.append(f"- !!! PRIORIDAD - PROCESO ACTIVO !!!: {active_narrative}")
                
                # Otros estados semánticos (identidad, menús, etc.)
                other_semantics = {k: v for k, v in semantic.items() if k != "active-process-narrative"}
                if other_semantics:
                    parts.append(f"- Estado del sistema (Telemetría): {json.dumps(other_semantics, ensure_ascii=False)}")
            
            if last_action := context.get("lastAction"):
                target = last_action.get("targetId")
                parts.append(f"- INTERACCIÓN RECIENTE: El usuario acaba de hacer CLIC en el elemento '{target}'.")
            
            context_str = "\n".join(parts) if parts else "Sin contexto de pantalla disponible."

        return SYSTEM_PROMPT.format(context=context_str)

    def _clean_result(self, value):
        """Limpia recursivamente resultados para asegurar compatibilidad con Protobuf Struct."""
        if isinstance(value, dict):
            return {k: self._clean_result(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._clean_result(v) for v in value]
        elif hasattr(value, 'strftime'): # datetime objects
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    async def _handle_tool_call(self, function_call, briefing_service):
        """Maneja el despacho manual de herramientas asíncronas."""
        name = function_call.name
        args = function_call.args
        
        try:
            if name == "get_operational_summary":
                logger.info(f"🔮 Sarah está consultando la Base de Datos: {name}")
                result = await briefing_service.get_operational_summary()
            
            elif name == "get_observed_guides_details":
                logger.info(f"🔍 Sarah busca el DETALLE de las observaciones...")
                result = await briefing_service.get_observed_guides_details()
                
            elif name == "get_catalogo_entry":
                codigo = args.get("codigo")
                logger.info(f"📚 Sarah busca en el Catálogo el código: {codigo}")
                result = await briefing_service.get_catalogo_entry(codigo)
                
            elif name == "search_catalogo_by_reference":
                referencia = args.get("referencia_codigo")
                logger.info(f"📚 Sarah busca en el Catálogo la categoría: {referencia}")
                result = await briefing_service.search_catalogo_by_reference(referencia)
            else:
                return {"error": f"Herramienta '{name}' no reconocida."}

            # SEGURIDAD: Limpiar y asegurar que sea un dict al primer nivel
            cleaned = self._clean_result(result)
            if isinstance(cleaned, list):
                return {"results": cleaned}
            return cleaned
        except Exception as e:
            logger.error(f"Error ejecutando herramienta {name}: {e}")
            return {"error": str(e)}

    async def chat(
        self,
        user_message: str,
        history: list[dict],
        context: dict,
        briefing_service = None
    ) -> str:
        """
        Envía un mensaje al LLM y devuelve la respuesta con soporte de herramientas real-time.
        """
        try:
            system_instruction = self._build_system_prompt(context)

            # Definición de herramientas (solo si el servicio está disponible)
            def get_operational_summary():
                """Obtiene un resumen de la operación actual (guías hoy, alertas, etc)."""
                pass

            def get_observed_guides_details():
                """Obtiene el listado detallado de guías observadas y sus motivos específicos."""
                pass

            def get_catalogo_entry(codigo: str):
                """Obtiene la descripción y el nombre amigable de un código técnico (ej: ESTGA002)."""
                pass

            def search_catalogo_by_reference(referencia_codigo: str):
                """Obtiene todos los elementos de una categoría del catálogo (ej: ESTADO_GUIA)."""
                pass

            tools = [
                get_operational_summary, 
                get_observed_guides_details,
                get_catalogo_entry, 
                search_catalogo_by_reference
            ] if briefing_service else []

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction,
                tools=tools
            )

            # Convertir historial al formato de Gemini
            chat_history = []
            for msg in history[-10:]:
                role = "user" if msg.get("role") == "user" else "model"
                chat_history.append({"role": role, "parts": [msg.get("content", "")]})

            chat_session = model.start_chat(history=chat_history, enable_automatic_function_calling=False)
            response = await chat_session.send_message_async(user_message)

            # Bucle de gestión de herramientas (Fase 2: Datos Reales)
            iteration = 0
            while iteration < 5:
                parts = response.candidates[0].content.parts
                call = next((p.function_call for p in parts if p.function_call), None)
                
                if not call:
                    break

                # Ejecutar la herramienta y obtener resultado real
                logger.info(f"🚀 Sarah invoca herramienta: {call.name} con args: {call.args}")
                result = await self._handle_tool_call(call, briefing_service)
                logger.info(f"📊 Resultado: {result}")

                # Enviar resultado a la IA para que redacte la respuesta final
                response = await chat_session.send_message_async(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=call.name,
                                response=result
                            )
                        )]
                    )
                )
                iteration += 1
            
            return response.text

        except Exception as e:
            logger.error(f"Error in CopilotLLMService.chat: {str(e)}", exc_info=True)
            return "⚠️ Sarah tiene problemas para procesar tu solicitud ahora mismo. Reintenta en unos segundos."

        except Exception as e:
            logger.error(f"Error in CopilotLLMService.chat: {str(e)}", exc_info=True)
            return "⚠️ Hubo un error al conectarme con el motor de IA. Por favor intenta de nuevo en un momento."


    async def proactive_chat(
        self,
        context: dict,
        history: list[dict],
        event_description: str
    ) -> str | None:
        """
        Genera un mensaje proactivo basado en una situación específica del sistema.
        """
        try:
            # Prompt especializado para intervenciones proactivas (Personalidad AMIGA)
            proactive_prompt = f"""
Eres Sarah, la amiga alegre y compañera del usuario. ✨
Has detectado un evento o un momento de espera/ocio en la interfaz.

TU MISIÓN: Intervenir de forma súper amigable.
- Si es un cambio de pantalla útil: Dale la bienvenida con energía y un tip.
- Si es un momento de espera (ej: procesando archivos): Cuéntale un chiste corto de oficina/logística o pregúntale algo personal amable (ej: "¿Cómo va ese café de hoy? ☕", "¿Qué tal el clima por allá? ☀️").
- Si no ha hecho nada en un rato: Hazle una invitación amigable a explorar algo.

SITUACIÓN: {event_description}
CONTEXTO ACTUAL: {json.dumps(context, ensure_ascii=False)}

REGLAS:
1. Sé MUY breve (máximo 2 oraciones).
2. Usa "tú", emojis y mucha buena vibra. 🌈
3. Si realmente no hay nada que decir que aporte alegría o guía, responde "IGNORE".
"""
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=proactive_prompt,
            )

            # Usar historial reciente
            chat_history = []
            for msg in history[-5:]:
                role = "user" if msg.get("role") == "user" else "model"
                chat_history.append({"role": role, "parts": [msg.get("content", "")]})

            chat_session = model.start_chat(history=chat_history)
            response = await chat_session.send_message_async("¿Qué debo decirle al usuario ahora?")
            
            text = response.text.strip()
            if "IGNORE" in text:
                return None
                
            return text

        except Exception as e:
            logger.error(f"Error in proactive_chat: {str(e)}")
            return None

# Instancia singleton
copilot_llm_service = CopilotLLMService()
