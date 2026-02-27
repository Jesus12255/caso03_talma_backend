from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
from app.core.websockets.manager import manager
from app.auth.dependencies.dependencies_auth import verify_websocket_token
from app.core.websockets.copilot.llm_service import copilot_llm_service
from config.database_config import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/copilot",
    tags=["Copilot AI"]
)

@router.websocket("/ws")
async def websocket_copilot_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for the AI Copilot.
    Requires a valid JWT token passed as a query parameter (?token=...).
    
    Incoming message format:
    {
        "action": "CHAT",
        "content": "mensaje del usuario",
        "context": {              # Contexto de la UI (Tarea 1.5)
            "route": "/risk-dashboard",
            "selectedFilters": {"status": "blocked"},
            "visibleEntities": ["awb_3321"],
            "activeModule": "Trazabilidad"
        },
        "history": [              # Historial de la conversación
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """
    try:
        user = await verify_websocket_token(token)
        if not user:
            await websocket.close(code=1008)
            return

        user_id = str(user.get("user_id", "unknown"))
        await manager.connect(websocket, user_id)
        logger.info(f"Copilot WebSocket connected for user: {user_id}")

        # Estado de sesión local para detectar cambios
        session_state = {"last_route": None}

        # Bucle principal
        while True:
            data = await websocket.receive_text()

            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                payload = {"action": "CHAT", "content": data}

            action = payload.get("action", "CHAT")
            context = payload.get("context", {})
            history = payload.get("history", [])

            # --- MANEJO DE SINCRONIZACIÓN SILENCIOSA ---
            # Solo actualiza el estado de sesión. Sin mensajes automáticos.
            if action == "SYNC_CONTEXT":
                new_route = context.get("route")
                if new_route:
                    session_state["last_route"] = new_route
                continue

            # --- MANEJO DE CHAT CONVENCIONAL ---
            user_message = payload.get("content", "").strip()
            if not user_message:
                continue

            logger.info(f"Copilot [{user_id}] action={action} route={context.get('route', '?')}")

            # Señal "escribiendo..."
            await websocket.send_text(json.dumps({"type": "signal", "status": "typing"}))

            # Llamada al LLM con acceso a datos reales
            async for db in get_db():
                # Instanciar el servicio de briefing manualmente (ya que estamos fuera de Depends)
                from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
                from app.core.repository.impl.perfil_riesgo_repository_impl import PerfilRiesgoRepositoryImpl
                from app.configuration.repository.impl.catalogo_repository_impl import CatalogoRepositoryImpl
                from app.core.services.impl.briefing_service_impl import BriefingServiceImpl
                
                doc_repo = DocumentRepositoryImpl(db)
                risk_repo = PerfilRiesgoRepositoryImpl(db)
                cat_repo = CatalogoRepositoryImpl(db)
                briefing_service = BriefingServiceImpl(doc_repo, risk_repo, cat_repo)

                ai_response = await copilot_llm_service.chat(
                    user_message=user_message,
                    history=history,
                    context=context,
                    briefing_service=briefing_service
                )
                break # Solo necesitamos una iteración del generador

            await websocket.send_text(json.dumps({
                "type": "message",
                "role": "assistant",
                "content": ai_response
            }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"Copilot WebSocket disconnected: {user_id}")
    except Exception as e:
        logger.error(f"Copilot WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
