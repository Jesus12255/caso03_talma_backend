from app.core.services.notificacion_service import NotificacionService
from app.core.services.audit_service import AuditService
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from app.core.services.guia_aerea_interviniente_service import GuiaAereaIntervinienteService
from app.integration.service.embedding_service import EmbeddingService
from dto.perfil_riesgo_dtos import PerfilRiesgoFiltroRequest
import unicodedata
from uuid import UUID
from datetime import datetime, timedelta
import math
from app.core.services.IrregularidadService import IrregularidadService
from app.core.repository.perfil_riesgo_repository import PerfilRiesgoRepository
from app.core.repository.notificacion_repository import NotificacionRepository
from app.core.repository.document_repository import DocumentRepository 
from app.core.domain.perfil_riesgo import PerfilRiesgo
from app.core.domain.guia_aerea import GuiaAerea
from app.core.domain.notificacion import Notificacion
from utl.constantes import Constantes
from core.realtime.publisher import  publish_user_notification
import logging

logger = logging.getLogger(__name__)
class IrregularidadServiceImpl(IrregularidadService):
    
    def __init__(self, 
        perfil_repo: PerfilRiesgoRepository,
        notificacion_repo: NotificacionRepository,
        notificacion_service: NotificacionService,
        document_repo: DocumentRepository,
        guia_aerea_interviniente_service: GuiaAereaIntervinienteService,
        embedding_service: EmbeddingService,
        auditoria_service: AuditService):
        self.perfil_repo = perfil_repo
        self.notificacion_repo = notificacion_repo
        self.document_repo = document_repo
        self.embedding_service = embedding_service
        self.guia_aerea_interviniente_service = guia_aerea_interviniente_service
        self.auditoria_service = auditoria_service
        self.notificacion_service = notificacion_service

    async def detectar_irregularidades(self, guia_aerea: GuiaAerea, analisis_contextual: dict = None) -> dict:
        total_score = 0
        alertas = []
        
      
        if analisis_contextual:
            es_ilegal = analisis_contextual.get("esIlegal", False)
            tiene_inconsistencias = analisis_contextual.get("tieneInconsistencias", False)
            irregularidades_ia = analisis_contextual.get("irregularidades", [])

            if es_ilegal:
                logger.warning(f"GATE-1 LEGAL: Guía {guia_aerea.numero} flagged como ILEGAL por IA")
                mensaje = f"Se detectaron irregularidades legales en la guía N°{guia_aerea.numero}: " + "; ".join(irregularidades_ia)
                await self._registrar_notificacion_ia(
                    guia_aerea,
                    titulo="Alerta de Riesgo Legal Detectada",
                    mensaje=mensaje[:197] + "..." if len(mensaje) > 200 else mensaje,
                    severidad=Constantes.SeveridadNotificacion.CRITICAL,
                    irregularidades=irregularidades_ia
                )
                return {"score": 100, "alertas": irregularidades_ia, "nivel_riesgo": "ALTO"}

            if tiene_inconsistencias:
                logger.warning(f"GATE-2 INCONSISTENCIA: Guía {guia_aerea.numero} tiene inconsistencias de negocio")
                mensaje = f"Se detectaron inconsistencias en la guía N°{guia_aerea.numero}: " + "; ".join(irregularidades_ia)
                await self._registrar_notificacion_ia(
                    guia_aerea,
                    titulo="Inconsistencias de Datos Detectadas",
                    mensaje=mensaje[:197] + "..." if len(mensaje) > 200 else mensaje,
                    severidad=Constantes.SeveridadNotificacion.WARNING,
                    irregularidades=irregularidades_ia
                )
                return {"score": 60, "alertas": irregularidades_ia, "nivel_riesgo": "MEDIO"}

        intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia_aerea.guia_aerea_id)
        remitente = next((i for i in intervinientes if i.rol_codigo == Constantes.TipoInterviniente.REMITENTE), None)
        consignatario = next((i for i in intervinientes if i.rol_codigo == Constantes.TipoInterviniente.CONSIGNATARIO), None)

        sender_score, sender_alerts = await self._analizar_remitente(remitente, guia_aerea)
        total_score += sender_score
        alertas.extend(sender_alerts)
   

        consignee_score, consignee_alerts = await self._analizar_consignatario(consignatario, guia_aerea)
        total_score += consignee_score
        alertas.extend(consignee_alerts)
        
        result = {
            "score": min(total_score, 100), 
            "alertas": alertas,
            "nivel_riesgo": self._determinar_nivel(total_score)
        }
       
        if total_score >= 30:
            await self._registrar_notificacion(guia_aerea, result)
        else: 
            await self.validar(guia_aerea)
            await publish_user_notification(str(guia_aerea.usuario_id), "SUCCESS", f"Guía aérea N°{guia_aerea.numero}: Procesado correctamente", str(guia_aerea.guia_aerea_id))
        return result

    async def _analizar_remitente(self, t: GuiaAereaInterviniente, guia: GuiaAerea) -> tuple[int, list]:
        score = 0
        alerts = []
     
        vector_nombre = await self.embedding_service.get_embedding(t.nombre)
        perfil = await self.perfil_repo.find_by_vector_similarity(vector_nombre, Constantes.TipoInterviniente.REMITENTE, threshold=0.1)

        if perfil:
            if perfil.score_base >= 100:
                score += perfil.score_base
                alerts.append(f"ALERTA CRÍTICA: El remitente '{t.nombre}' se encuentra en la LISTA NEGRA del sistema.")
            else:
                score += perfil.score_base
                if perfil.cantidad_envios >= 4 and perfil.peso_std_dev > 0:
                    score, alerts = await self._calcula_puntuacion_z_peso(perfil, guia, score, alerts)
                    score, alerts = await self._analizar_ruta(perfil, guia, score, alerts)
                
        return score, alerts

    async def _analizar_consignatario(self, t: GuiaAereaInterviniente, guia: GuiaAerea) -> tuple[int, list]:
        score = 0
        alerts = []
        
        vector = await self.embedding_service.get_embedding(t.nombre)
        perfil = await self.perfil_repo.find_by_vector_similarity(vector, Constantes.TipoInterviniente.CONSIGNATARIO, threshold=0.1)
        
        if not perfil: 
            return score, alerts

        score += perfil.score_base
        nombres_busqueda = await self._crea_lista_de_nombres_del_consignatario(t, perfil)
        recent_shipments = await self.document_repo.find_recent_by_consignee_names(nombres_busqueda, hours=24)
        count = len(recent_shipments)
        
        tolerancia = perfil.factor_tolerancia or 1.0
        limit_pitufeo   = 4 * tolerancia
        limit_frecuencia = 2 * tolerancia

        if count > limit_pitufeo:
            score += Constantes.PuntuacionNivelRiesgo.ALTO
            alerts.append(
                f"Posible fraccionamiento de envíos (pitufeo): el consignatario '{t.nombre}' "
                f"registra {count} guías en las últimas 24 h, superando el límite permitido de {int(limit_pitufeo)}."
            )
        elif count > limit_frecuencia:
            score += Constantes.PuntuacionNivelRiesgo.MEDIO
            alerts.append(
                f"Frecuencia de recepción elevada: el consignatario '{t.nombre}' "
                f"acumula {count} guías en las últimas 24 h (límite habitual: {int(limit_frecuencia)})."
            )

        if perfil.score_base >= 100:
            alerts.append(f"ALERTA CRÍTICA: El consignatario '{t.nombre}' se encuentra en la LISTA NEGRA del sistema.")
            
        return score, alerts

    async def _crea_lista_de_nombres_del_consignatario(self, t: GuiaAereaInterviniente, perfil: PerfilRiesgo) -> list[str]:
        nombres_busqueda = [t.nombre]
        if perfil and perfil.variaciones_nombre:
            nombres_busqueda.extend(perfil.variaciones_nombre)
            nombres_busqueda = list(set(nombres_busqueda))
        return nombres_busqueda

    async def _calcula_puntuacion_z_peso(self, perfil: PerfilRiesgo, guia: GuiaAerea, score: int, alerts: list) -> tuple[int, list]:
        current_weight = float(guia.peso_bruto or 0)
        
        # Matemáticas Z-Score tradicionales
        # Prevenir división por cero usando un mínimo de 1.0 kg de desviación estándar
        std_dev_seguro = max(perfil.peso_std_dev, 1.0)
        
        z_score     = (current_weight - perfil.peso_promedio) / std_dev_seguro
        z_abs       = abs(z_score)
        direccion   = "mayor" if z_score > 0 else "menor"

        tolerancia  = perfil.factor_tolerancia or 1.0
        limit_alto  = 3 * tolerancia
        limit_medio = 2 * tolerancia

        # ── Regla 1: Z-score (bidireccional) ─────────────────────────────────
        if z_abs > limit_alto:
            score += Constantes.PuntuacionNivelRiesgo.ALTO
            alerts.append(
                f"Peso muy inusual para este remitente: la guía declara {current_weight:.2f} kg, "
                f"significativamente {direccion} al promedio histórico de {perfil.peso_promedio:.2f} kg "
                f"(desviación Z = {z_score:.1f}). Podría indicar {'sobrecarga no declarada' if z_score > 0 else 'subdeclaración de carga'}."
            )
        elif z_abs > limit_medio:
            score += Constantes.PuntuacionNivelRiesgo.MEDIO
            alerts.append(
                f"Peso atípico para este remitente: la guía declara {current_weight:.2f} kg, "
                f"{direccion} al promedio histórico de {perfil.peso_promedio:.2f} kg "
                f"(desviación Z = {z_score:.1f})."
            )

        # ── Regla 2: porcentaje del promedio (protección en perfiles jóvenes) ─
        # Actúa cuando el Z-score no fue suficiente (perfil con alta dispersión)
        # y el peso es absurdamente bajo respecto al histórico del remitente.
        elif perfil.peso_promedio > 0 and current_weight < perfil.peso_promedio:
            ratio = current_weight / perfil.peso_promedio  # ej: 0.17 = 17%
            if ratio < 0.10:
                score += Constantes.PuntuacionNivelRiesgo.ALTO
                alerts.append(
                    f"Peso extremadamente bajo para este remitente: la guía declara {current_weight:.2f} kg, "
                    f"que representa solo el {ratio*100:.0f}% del peso promedio histórico ({perfil.peso_promedio:.2f} kg). "
                    f"Alta sospecha de subdeclaración de carga."
                )
            elif ratio < 0.20:
                score += Constantes.PuntuacionNivelRiesgo.MEDIO
                alerts.append(
                    f"Peso inusualmente bajo para este remitente: la guía declara {current_weight:.2f} kg, "
                    f"que es solo el {ratio*100:.0f}% del peso promedio histórico ({perfil.peso_promedio:.2f} kg). "
                    f"Posible subdeclaración de carga."
                )

        return score, alerts



    async def _analizar_ruta(self, perfil: PerfilRiesgo, guia: GuiaAerea, score: int, alerts: list) -> tuple[int, list]:
        ruta_key = f"{guia.origen_codigo}-{guia.destino_codigo}"
        rutas_conocidas = list((perfil.rutas_frecuentes or {}).keys())
        if perfil.rutas_frecuentes and ruta_key not in perfil.rutas_frecuentes:
            score += Constantes.PuntuacionNivelRiesgo.MEDIO
            alerts.append(
                f"Ruta no registrada en el historial del remitente: la ruta {guia.origen_codigo} → {guia.destino_codigo} "
                f"nunca ha sido utilizada antes. Rutas habituales: {', '.join(rutas_conocidas) or 'ninguna registrada'}."
            )

        return score, alerts

    async def _crear_nuevo_perfil(self, t: GuiaAereaInterviniente, vector: list, guia: GuiaAerea) -> PerfilRiesgo:
        current_weight = float(guia.peso_bruto or 0)
        ruta_key = f"{guia.origen_codigo}-{guia.destino_codigo}"
        current_date = guia.fecha_vuelo
    
        perfil = PerfilRiesgo(
            nombre_normalizado= self._normalize_name(t.nombre),
            tipo_interviniente_codigo=t.rol_codigo,
            variaciones_nombre=[t.nombre],
            telefonos_conocidos=[t.telefono] if t.telefono else [],
            direcciones_conocidas=[t.direccion] if t.direccion else [],
            vector_identidad=vector,
            peso_promedio=0.0,
            peso_std_dev=0.0,
            peso_maximo_historico=0.0,
            peso_minimo_historico=0.0,
            cantidad_envios=0,
            rutas_frecuentes={},
            fecha_primer_envio=current_date,
            fecha_ultimo_envio=current_date,
            total_consignatarios_vinculados=0, 
            modificado=datetime.now()
        )
        await self.perfil_repo.save(perfil)
        return perfil

    async def _actualizar_estadisticas_perfil(self, perfil: PerfilRiesgo, guia: GuiaAerea, nombre: str):
       
        current_weight = float(guia.peso_bruto or 0)
        current_date = guia.fecha_vuelo
        ruta_key = f"{guia.origen_codigo}-{guia.destino_codigo}"
        n = perfil.cantidad_envios
        old_avg = perfil.peso_promedio
        new_avg = ((old_avg * n) + current_weight) / (n + 1)
        
        old_var = perfil.peso_std_dev ** 2
        if n > 0:
            new_var = ((n * old_var) + (current_weight - new_avg) * (current_weight - old_avg)) / (n + 1)
            perfil.peso_std_dev = math.sqrt(new_var)
        perfil.peso_promedio = new_avg
        perfil.cantidad_envios += 1
        
        rutas = dict(perfil.rutas_frecuentes or {})
        rutas[ruta_key] = rutas.get(ruta_key, 0) + 1
        perfil.rutas_frecuentes = rutas
        
        if current_weight > (perfil.peso_maximo_historico or 0):
            perfil.peso_maximo_historico = current_weight
            
        # Para el peso mínimo comprobamos que si es el primer envío (el actual mínimo puede ser 0 o estar mal asignado) 
        # o si es menor al que tenemos guardado, lo reemplazamos.
        if perfil.cantidad_envios == 1 or current_weight < (perfil.peso_minimo_historico or float('inf')) or (perfil.peso_minimo_historico == 0 and current_weight > 0):
             perfil.peso_minimo_historico = current_weight

        # Actualizamos fechas extremas del ciclo de vida operativo de forma robusta
        if not perfil.fecha_primer_envio or current_date < perfil.fecha_primer_envio:
            perfil.fecha_primer_envio = current_date
            
        if not perfil.fecha_ultimo_envio or current_date > perfil.fecha_ultimo_envio:
            perfil.fecha_ultimo_envio = current_date

        # Calculamos los días promedio entre envío basándonos en la ventana total de tiempo
        if perfil.cantidad_envios > 1 and perfil.fecha_primer_envio and perfil.fecha_ultimo_envio:
            total_dias = (perfil.fecha_ultimo_envio - perfil.fecha_primer_envio).days
            perfil.dias_promedio_entre_envios = int(round(total_dias / (perfil.cantidad_envios - 1)))

        perfil.modificado = datetime.now()
        
        
        variaciones = list(perfil.variaciones_nombre or [])
        if nombre not in variaciones:
                variaciones.append(nombre)
                perfil.variaciones_nombre = variaciones

        await self.perfil_repo.update(perfil.perfil_riesgo_id, perfil)

        
        intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia.guia_aerea_id)
        interviniente = next((i for i in intervinientes if i.rol_codigo == perfil.tipo_interviniente_codigo), None)

        if interviniente:
             if interviniente.telefono and interviniente.telefono not in (perfil.telefonos_conocidos or []):
                  telefonos = list(perfil.telefonos_conocidos or [])
                  telefonos.append(interviniente.telefono)
                  perfil.telefonos_conocidos = telefonos
                  
             if interviniente.direccion and interviniente.direccion not in (perfil.direcciones_conocidas or []):
                  direcciones = list(perfil.direcciones_conocidas or [])
                  direcciones.append(interviniente.direccion)
                  perfil.direcciones_conocidas = direcciones

        
        if perfil.tipo_interviniente_codigo == Constantes.TipoInterviniente.REMITENTE:
             count = await self.document_repo.count_unique_consignees_for_sender(perfil.variaciones_nombre or [nombre])
             perfil.total_consignatarios_vinculados = count
             
        await self.perfil_repo.update(perfil.perfil_riesgo_id, perfil)

    def _determinar_nivel(self, score: int) -> str:
        if score < 40: return "BAJO"
        if score < 75: return "MEDIO"
        return "ALTO"

    async def _registrar_notificacion(self, guia: GuiaAerea, result: dict):
        is_blacklist = any("LISTA NEGRA" in a for a in result['alertas'])
        mensaje_notif = f"Se detectaron {len(result['alertas'])} alertas. Score: {result['score']}"
        titulo_notif = f"Irregularidad Detectada: {result['nivel_riesgo']}"
        severidad_notif = Constantes.SeveridadNotificacion.WARNING if result['score'] < 75 else Constantes.SeveridadNotificacion.CRITICAL

        if is_blacklist:
            mensaje_notif = "No se puede procesar porque alguno de los intervinientes está en la lista negra"
            titulo_notif = "BLOQUEO: Interviniente en Lista Negra"
            severidad_notif = Constantes.SeveridadNotificacion.CRITICAL

        notificacion = Notificacion(
            guia_aerea_id=guia.guia_aerea_id,
            usuario_id=guia.usuario_id,
            tipo_codigo=Constantes.TipoNotificacion.IRREGULARIDAD,
            titulo=titulo_notif,
            mensaje=mensaje_notif,
            severidad_codigo=severidad_notif,
            estado_codigo=Constantes.EstadoNotificacion.PENDIENTE,
            meta_data={
                "score_riesgo": result['score'],
                "alertas": result['alertas'],
                "nivel": result['nivel_riesgo'],
                "is_blacklist": is_blacklist
            }
        )
        await self.notificacion_repo.save(notificacion)

        severity_label = "CRITICAL" if notificacion.severidad_codigo == Constantes.SeveridadNotificacion.CRITICAL else "WARNING"
        await publish_user_notification(
            user_id=str(guia.usuario_id), 
            type=notificacion.tipo_codigo, # Pass correct type (TPN004)
            message=notificacion.mensaje,   # Pass the message body
            title=notificacion.titulo,      # Pass the title
            doc_id=str(guia.guia_aerea_id),
            severity=severity_label,
            is_persistent=True,             # It's an important notification
            notification_id=str(notificacion.notificacion_id),
            metadata=notificacion.meta_data # Pass the metadata!
        )

        update_data = {
                "estado_registro_codigo": Constantes.EstadoRegistroGuiaAereea.OBSERVADO,
                "modificado": datetime.now(),
                "modificado_por": Constantes.SYSTEM_USER
            }
        
        if is_blacklist:
            update_data["observaciones"] = "No se puede procesar porque alguno de los intervinientes está en la lista negra"

        await self.document_repo.update(guia.guia_aerea_id, update_data)

        await self.auditoria_service.registrar_modificacion(
                    entidad_tipo=Constantes.TipoEntidadAuditoria.GUIA_AEREA,
                    entidad_id=guia.guia_aerea_id,
                    numero_documento=guia.numero,
                    campo="estado_registro_codigo",
                    valor_anterior="PROCESANDO",
                    valor_nuevo="OBSERVADO"
                )

    async def _registrar_notificacion_ia(
        self,
        guia: GuiaAerea,
        titulo: str,
        mensaje: str,
        severidad: str,
        irregularidades: list
    ):
        """Registra notificación generada por el análisis contextual de la IA."""
        import uuid as uuid_module
        notificacion = Notificacion(
            notificacion_id=uuid_module.uuid4(),
            guia_aerea_id=guia.guia_aerea_id,
            usuario_id=guia.usuario_id,
            tipo_codigo=Constantes.TipoNotificacion.IRREGULARIDAD,
            titulo=titulo,
            mensaje=mensaje,
            severidad_codigo=severidad,
            estado_codigo=Constantes.EstadoNotificacion.PENDIENTE,
            meta_data={
                "alertas": irregularidades,
                "nivel": "ALTO" if severidad == Constantes.SeveridadNotificacion.CRITICAL else "MEDIO",
                "score_riesgo": 100 if severidad == Constantes.SeveridadNotificacion.CRITICAL else 60,
                "fuente": "ANALISIS_IA"
            }
        )
        notificacion.habilitado = Constantes.HABILITADO
        await self.notificacion_repo.save(notificacion)

        severity_label = "CRITICAL" if severidad == Constantes.SeveridadNotificacion.CRITICAL else "WARNING"
        await publish_user_notification(
            user_id=str(guia.usuario_id),
            type=Constantes.TipoNotificacion.IRREGULARIDAD,
            message=mensaje,
            title=titulo,
            doc_id=str(guia.guia_aerea_id),
            severity=severity_label,
            is_persistent=True,
            notification_id=str(notificacion.notificacion_id),
            metadata=notificacion.meta_data
        )

        await self.document_repo.update(guia.guia_aerea_id, {
            "estado_registro_codigo": Constantes.EstadoRegistroGuiaAereea.OBSERVADO,
            "modificado": datetime.now(),
            "modificado_por": Constantes.SYSTEM_USER
        })

        await self.auditoria_service.registrar_modificacion(
            entidad_tipo=Constantes.TipoEntidadAuditoria.GUIA_AEREA,
            entidad_id=guia.guia_aerea_id,
            numero_documento=guia.numero,
            campo="estado_registro_codigo",
            valor_anterior="PROCESANDO",
            valor_nuevo="OBSERVADO"
        )

    async def validarExcepcion(self, notificacion_id: UUID):
        notificacion = await self.notificacion_service.get(notificacion_id)
        guia = await self.document_repo.get_by_id(notificacion.guia_aerea_id)
        
        # Analizar el tipo de alertas que generaron esta notificación
        alertas = notificacion.meta_data.get("alertas", []) if notificacion.meta_data else []
        hubo_alerta_peso = any("Peso" in a or "Z-score" in a or "subdeclaración" in a for a in alertas)
        hubo_alerta_frecuencia = any("pitufeo" in a or "Frecuencia" in a for a in alertas)

        # Aprendizaje Reforzado Dirigido
        intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia.guia_aerea_id)
        
        for t in intervinientes:
             vector = await self.embedding_service.get_embedding(t.nombre)
             perfil = await self.perfil_repo.find_by_vector_similarity(vector, t.rol_codigo, threshold=0.1)
             
             if perfil:
                 modificado = False
                 # Si la alerta fue por peso y este es el remitente (quien despacha el peso), se amplía tolerancia
                 if hubo_alerta_peso and t.rol_codigo == Constantes.TipoInterviniente.REMITENTE:
                     perfil.factor_tolerancia = (perfil.factor_tolerancia or 1.0) + 0.5
                     modificado = True
                     
                 # Si la alerta fue por frecuencia (pitufeo) y este es el consignatario (quien recibe repetidamente)
                 if hubo_alerta_frecuencia and t.rol_codigo == Constantes.TipoInterviniente.CONSIGNATARIO:
                     perfil.factor_tolerancia = (perfil.factor_tolerancia or 1.0) + 0.5
                     modificado = True
                     
                 if modificado:
                     await self.perfil_repo.update(perfil.perfil_riesgo_id, perfil)
                 
        await self.validar(guia)
        await self.notificacion_service.resolver(guia.guia_aerea_id)
        await self.auditoria_service.registrar_modificacion(
            entidad_tipo=Constantes.TipoEntidadAuditoria.GUIA_AEREA,
            entidad_id=guia.guia_aerea_id,
            numero_documento=guia.numero,
            campo="estado_registro_codigo",
            valor_anterior="OBSERVADO",
            valor_nuevo="PROCESADO",
            comentario="Validación de excepción de irregularidad (Aprendizaje reforzado -> Hubo ampliación de tolerancia del Perfil)"
        )
        await publish_user_notification(
            user_id=str(notificacion.usuario_id), 
            type="SUCCESS", 
            message=f"Guía N°{guia.numero} validada y procesada correctamente.",   
            title="Excepción Validada",      
            doc_id=str(guia.guia_aerea_id),
            severity="INFO",
            is_persistent=False
        )
        return guia

    async def validar(self, guia: GuiaAerea ):
        intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia.guia_aerea_id)
        
        for t in intervinientes:
             vector = await self.embedding_service.get_embedding(t.nombre)
             perfil = await self.perfil_repo.find_by_vector_similarity(vector, t.rol_codigo, threshold=0.1)
             
             if not perfil:
                 perfil = await self._crear_nuevo_perfil(t, vector, guia)
                 
             if perfil:
                 await self._actualizar_estadisticas_perfil(perfil, guia, t.nombre)

        update_data = {
            "estado_registro_codigo": Constantes.EstadoRegistroGuiaAereea.PROCESADO,
            "modificado": datetime.now(),
            "modificado_por": Constantes.SYSTEM_USER
        }
        await self.document_repo.update(guia.guia_aerea_id, update_data)

    def _normalize_name(self, nombre: str) -> str:   
        if not nombre:
            return ""
        nfkd_form = unicodedata.normalize('NFKD', nombre)
        nombre_sin_tildes = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        normalized = nombre_sin_tildes.upper().strip()
        return " ".join(normalized.split())

    async def getRedVinculos(self, request: PerfilRiesgoFiltroRequest) -> "RedVinculosResponse":
        from dto.perfil_riesgo_dtos import RedVinculosResponse, GrafoNodo, GrafoArco
        # Coordenadas estáticas de aeropuertos principales
        IATA_COORDS = {
            "LIM": {"lat": -12.0219, "lng": -77.1143, "name": "Lima (LIM)"},
            "MIA": {"lat": 25.7959, "lng": -80.2870, "name": "Miami (MIA)"},
            "AMS": {"lat": 52.3105, "lng": 4.7683, "name": "Amsterdam (AMS)"},
            "MAD": {"lat": 40.4839, "lng": -3.5680, "name": "Madrid (MAD)"},
            "JFK": {"lat": 40.6413, "lng": -73.7781, "name": "New York (JFK)"},
            "LAX": {"lat": 33.9416, "lng": -118.4085, "name": "Los Angeles (LAX)"},
            "BOG": {"lat": 4.7016, "lng": -74.1469, "name": "Bogota (BOG)"},
            "SCL": {"lat": -33.3930, "lng": -70.7858, "name": "Santiago (SCL)"},
            "GRU": {"lat": -23.4356, "lng": -46.4731, "name": "Sao Paulo (GRU)"},
            "YUL": {"lat": 45.4657, "lng": -73.7481, "name": "Montreal (YUL)"}
        }

        # Step 1: Calcular el rango de fechas para el filtro
        # Si no se proporcionan fechas, usamos las últimas 24 horas por defecto
        end_date = request.fechaFin or datetime.now()
        start_date = request.fechaInicio or (end_date - timedelta(hours=24))

        # Aseguramos que las fechas sean "naive" (sin zona horaria) para SQLAlchemy
        # ya que el modelo GuiaAerea usa TIMESTAMP sin zona horaria.
        if start_date and start_date.tzinfo:
            start_date = start_date.replace(tzinfo=None)
        if end_date and end_date.tzinfo:
            end_date = end_date.replace(tzinfo=None)

        # Step 1: Obtener las guías aéreas con sus intervinientes para el rango de fechas
        guias = await self.document_repo.find_by_date_range(
            start_date=start_date, 
            end_date=end_date,
            skip=request.start or 0, 
            limit=request.limit or 1000 # Aumentamos el límite para el mapa
        )
        
        nombres_perfil_filtro = None
        tipo_interviniente_filtro = None
        if getattr(request, 'perfilRiesgoId', None):
            try:
                perfil_id = UUID(request.perfilRiesgoId)
                perfil = await self.perfil_repo.get_by_id(perfil_id)
                if perfil:
                    nombres_perfil_filtro = perfil.variaciones_nombre or []
                    if perfil.nombre_normalizado and perfil.nombre_normalizado not in nombres_perfil_filtro:
                        nombres_perfil_filtro.append(perfil.nombre_normalizado)
                    tipo_interviniente_filtro = perfil.tipo_interviniente_codigo
            except Exception as e:
                logger.warning(f"Error loading Profile for Map Filter: {e}")

        nodes_dict = {}
        arcs_list = []
        
        # Primero aseguramos que todos los aeropuertos estén como nodos base
        for code, data in IATA_COORDS.items():
            nodes_dict[code] = GrafoNodo(
                id=code, name=data["name"], lat=data["lat"], lng=data["lng"], 
                type="airport", size=15, color="#4b5563"
            )

        # Para dispersión (jitter) visual para que las empresas no se monten exacto sobre el aeropuerto
        import random
        
        for guia in guias:
            origen = guia.origen_codigo or "LIM"
            destino = guia.destino_codigo or "MIA"
            
            if origen not in IATA_COORDS or destino not in IATA_COORDS:
                continue

            # Obtener intervinientes de esta específica guía
            intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia.guia_aerea_id)
            remitente = next((i for i in intervinientes if i.rol_codigo == Constantes.TipoInterviniente.REMITENTE), None)
            consignatario = next((i for i in intervinientes if i.rol_codigo == Constantes.TipoInterviniente.CONSIGNATARIO), None)

            if remitente and consignatario:
                rem_name = self._normalize_name(remitente.nombre)
                con_name = self._normalize_name(consignatario.nombre)
                
                if nombres_perfil_filtro and tipo_interviniente_filtro:
                    matches = False
                    if tipo_interviniente_filtro == Constantes.TipoInterviniente.REMITENTE:
                        if remitente.nombre in nombres_perfil_filtro or rem_name in nombres_perfil_filtro:
                            matches = True
                    elif tipo_interviniente_filtro == Constantes.TipoInterviniente.CONSIGNATARIO:
                        if consignatario.nombre in nombres_perfil_filtro or con_name in nombres_perfil_filtro:
                            matches = True
                    
                    if not matches:
                        continue
                
                # Crear nodos interactivos para las empresas si no existen:
                if rem_name not in nodes_dict:
                    nodes_dict[rem_name] = GrafoNodo(
                        id=rem_name, name=rem_name, 
                        lat=IATA_COORDS[origen]["lat"] + random.uniform(-1, 1), 
                        lng=IATA_COORDS[origen]["lng"] + random.uniform(-1, 1), 
                        type="sender", size=5, color="#3b82f6" # Azul
                    )
                else: 
                     nodes_dict[rem_name].size += 1

                if con_name not in nodes_dict:
                    nodes_dict[con_name] = GrafoNodo(
                        id=con_name, name=con_name, 
                        lat=IATA_COORDS[destino]["lat"] + random.uniform(-1, 1), 
                        lng=IATA_COORDS[destino]["lng"] + random.uniform(-1, 1), 
                        type="consignee", size=5, color="#10b981" # Verde
                    )
                else:
                     nodes_dict[con_name].size += 1

                color_arco = "#8b5cf6" # Default Purple
                if guia.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO:
                    color_arco = "#ef4444" # Red para sospechas
                
                # Diferenciación visual basada en peso
                peso = float(guia.peso_bruto or 0)
                # Stroke entre 0.5 y 2.5 según peso (Base 0.5 + logaritmo o escala simple)
                stroke_val = 0.5 + min(peso / 500, 2.0) 
                # Altitud con un toque de aleatoriedad para que no se peguen las líneas
                altitude_val = 0.1 + random.uniform(0.05, 0.4)

                arcs_list.append(GrafoArco(
                    id=str(guia.guia_aerea_id),
                    startLat=nodes_dict[rem_name].lat,
                    startLng=nodes_dict[rem_name].lng,
                    endLat=nodes_dict[con_name].lat,
                    endLng=nodes_dict[con_name].lng,
                    color=color_arco,
                    label=f"{rem_name} ➔ {con_name} ({guia.peso_bruto}kg)",
                    sender=rem_name,
                    consignee=con_name,
                    altitude=altitude_val,
                    stroke=stroke_val
                ))

        return RedVinculosResponse(
            nodes=list(nodes_dict.values()),
            arcs=arcs_list
        )