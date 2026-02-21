from app.core.services.notificacion_service import NotificacionService
from app.core.services.audit_service import AuditService
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
from app.core.services.guia_aerea_interviniente_service import GuiaAereaIntervinienteService
from app.integration.service.embedding_service import EmbeddingService
import unicodedata
from uuid import UUID
from datetime import datetime
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
       
        if total_score >= 40:
            await self._registrar_notificacion(guia_aerea, result)
        else: 
            update_data = {
                "estado_registro_codigo": Constantes.EstadoRegistroGuiaAereea.PROCESADO,
                "modificado": datetime.now(),
                "modificado_por": Constantes.SYSTEM_USER
            }
            await self.document_repo.update(guia_aerea.guia_aerea_id, update_data)
            await publish_user_notification(str(guia_aerea.usuario_id), "SUCCESS", f"Guía aérea N°{guia_aerea.numero}: Procesado correctamente", str(guia_aerea.guia_aerea_id))
        return result

    async def _analizar_remitente(self, t: GuiaAereaInterviniente, guia: GuiaAerea) -> tuple[int, list]:
        score = 0
        alerts = []
     
        vector_nombre = await self.embedding_service.get_embedding(t.nombre)
        perfil = await self.perfil_repo.find_by_vector_similarity(vector_nombre, Constantes.TipoInterviniente.REMITENTE, threshold=0.1)

        if not perfil:
            perfil = await self._crear_nuevo_perfil(t, vector_nombre, guia)
        else:
            score += perfil.score_base
            if perfil.cantidad_envios > 3 and perfil.peso_std_dev > 0:
                score, alerts = await self._calcula_puntuacion_z_peso(perfil, guia, score, alerts)
                score, alerts = await self._analizar_ruta(perfil, guia, score, alerts)
            if score == 0: 
                await self._actualizar_estadisticas_perfil(perfil, guia, t.nombre)
        return score, alerts

    async def _analizar_consignatario(self, t: GuiaAereaInterviniente, guia: GuiaAerea) -> tuple[int, list]:
        score = 0
        alerts = []
        
        vector = await self.embedding_service.get_embedding(t.nombre)
        perfil = await self.perfil_repo.find_by_vector_similarity(vector, Constantes.TipoInterviniente.CONSIGNATARIO, threshold=0.1)
        
        if not perfil: 
            await self._crear_nuevo_perfil(t, vector, guia)
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
        if score == 0: 
            await self._actualizar_estadisticas_perfil(perfil, guia, t.nombre)
        return score, alerts

    async def _crea_lista_de_nombres_del_consignatario(self, t: GuiaAereaInterviniente, perfil: PerfilRiesgo) -> list[str]:
        nombres_busqueda = [t.nombre]
        if perfil and perfil.variaciones_nombre:
            nombres_busqueda.extend(perfil.variaciones_nombre)
            nombres_busqueda = list(set(nombres_busqueda))
        return nombres_busqueda

    async def _calcula_puntuacion_z_peso(self, perfil: PerfilRiesgo, guia: GuiaAerea, score: int, alerts: list) -> tuple[int, list]:
        current_weight = float(guia.peso_bruto or 0)
        z_score     = (current_weight - perfil.peso_promedio) / perfil.peso_std_dev
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

    async def _crear_nuevo_perfil(self, t: GuiaAereaInterviniente, vector: list, guia: GuiaAerea):
        current_weight = float(guia.peso_bruto or 0)
        ruta_key = f"{guia.origen_codigo}-{guia.destino_codigo}"
    
        perfil = PerfilRiesgo(
            nombre_normalizado= self._normalize_name(t.nombre),
            tipo_interviniente_codigo=t.rol_codigo,
            variaciones_nombre=[t.nombre],
            telefonos_conocidos=[t.telefono] ,
            direcciones_conocidas=[t.direccion],
            vector_identidad=vector,
            peso_promedio=current_weight,
            peso_std_dev=0.0,
            peso_maximo_historico=current_weight,
            cantidad_envios=1,
            rutas_frecuentes={ruta_key: 1},
            fecha_primer_envio=datetime.now(),
            fecha_ultimo_envio=datetime.now(),
            total_consignatarios_vinculados=1 if t.rol_codigo == Constantes.TipoInterviniente.REMITENTE else 0, 
            modificado=datetime.now()
        )
        await self.perfil_repo.save(perfil)
        return perfil

    async def _actualizar_estadisticas_perfil(self, perfil: PerfilRiesgo, guia: GuiaAerea, nombre: str):
       
        current_weight = float(guia.peso_bruto or 0)
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

        perfil.fecha_ultimo_envio = datetime.now()
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
        notificacion = Notificacion(
            guia_aerea_id=guia.guia_aerea_id,
            usuario_id=guia.usuario_id,
            tipo_codigo=Constantes.TipoNotificacion.IRREGULARIDAD,
            titulo=f"Irregularidad Detectada: {result['nivel_riesgo']}",
            mensaje=f"Se detectaron {len(result['alertas'])} alertas. Score: {result['score']}",
            severidad_codigo=Constantes.SeveridadNotificacion.WARNING if result['score'] < 75 else Constantes.SeveridadNotificacion.CRITICAL,
            estado_codigo=Constantes.EstadoNotificacion.PENDIENTE,
            meta_data={
                "score_riesgo": result['score'],
                "alertas": result['alertas'],
                "nivel": result['nivel_riesgo']
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
        await self.validar(guia)
        await self.notificacion_service.resolver(guia.guia_aerea_id)
        await self.auditoria_service.registrar_modificacion(
            entidad_tipo=Constantes.TipoEntidadAuditoria.GUIA_AEREA,
            entidad_id=guia.guia_aerea_id,
            numero_documento=guia.numero,
            campo="estado_registro_codigo",
            valor_anterior="OBSERVADO",
            valor_nuevo="PROCESADO",
            comentario="Validación de excepción de irregularidad (Aprendizaje reforzado)"
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

    async def validar(self, guia: GuiaAerea ):
        intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia.guia_aerea_id)
        
        for t in intervinientes:
             vector = await self.embedding_service.get_embedding(t.nombre)
             perfil = await self.perfil_repo.find_by_vector_similarity(vector, t.rol_codigo, threshold=0.1)
             
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