from app.core.services.briefing_service import BriefingService
from app.core.repository.document_repository import DocumentRepository
from app.core.repository.perfil_riesgo_repository import PerfilRiesgoRepository
from app.configuration.repository.catalogo_repository import CatalogoRepository
from sqlalchemy import select, func
from app.core.domain.guia_aerea import GuiaAerea
from app.core.domain.perfil_riesgo import PerfilRiesgo
from app.configuration.domain.catalogo import Catalogo
from utl.constantes import Constantes
from datetime import datetime, time, timedelta
import logging

logger = logging.getLogger(__name__)

class BriefingServiceImpl(BriefingService):
    def __init__(
        self, 
        document_repository: DocumentRepository,
        perfil_riesgo_repository: PerfilRiesgoRepository,
        catalogo_repository: CatalogoRepository
    ):
        self.document_repository = document_repository
        self.perfil_riesgo_repository = perfil_riesgo_repository
        self.catalogo_repository = catalogo_repository

    async def get_operational_summary(self) -> dict:
        """
        Consulta la base de datos para obtener métricas reales.
        """
        try:
            # Consideramos "hoy" las últimas 24 horas o desde el inicio del día
            today_start = datetime.combine(datetime.now().date(), time.min)
            
            db = self.document_repository.db
            
            # 1. Estadísticas de Guías Aéreas
            q_total = select(func.count(GuiaAerea.guia_aerea_id)).where(
                GuiaAerea.creado >= today_start,
                GuiaAerea.habilitado == True
            )
            total_today = (await db.execute(q_total)).scalar() or 0
            
            q_observed = select(func.count(GuiaAerea.guia_aerea_id)).where(
                GuiaAerea.creado >= today_start,
                GuiaAerea.habilitado == True,
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            )
            observed_today = (await db.execute(q_observed)).scalar() or 0

            q_accepted = select(func.count(GuiaAerea.guia_aerea_id)).where(
                GuiaAerea.creado >= today_start,
                GuiaAerea.habilitado == True,
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.ACEPTADO
            )
            accepted_today = (await db.execute(q_accepted)).scalar() or 0
            
            # 2. Estadísticas de Riesgo
            db_risk = self.perfil_riesgo_repository.db
            q_risk = select(func.count(PerfilRiesgo.perfil_riesgo_id)).where(
                PerfilRiesgo.score_base >= 80,
                PerfilRiesgo.habilitado == True
            )
            critical_profiles = (await db_risk.execute(q_risk)).scalar() or 0

            return {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "total_guias_hoy": total_today,
                "guias_observadas": observed_today,
                "guias_aceptadas": accepted_today,
                "guias_limpias": total_today - observed_today,
                "perfiles_criticos": critical_profiles,
                "sistema_status": "OPERATIVO" if total_today > 0 else "SIN ACTIVIDAD RECIENTE"
            }
        except Exception as e:
            logger.error(f"Error generando briefing operativo: {e}")
            return {"error": "No se pudo obtener la información real en este momento."}

    async def get_observed_guides_details(self) -> list[dict]:
        """Obtiene el listado detallado de guías observadas y sus motivos."""
        try:
            today_start = datetime.combine(datetime.now().date(), time.min)
            db = self.document_repository.db
            
            # Consultar guías observadas de hoy con sus motivos
            query = select(GuiaAerea).where(
                GuiaAerea.creado >= today_start,
                GuiaAerea.habilitado == True,
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO
            ).order_by(GuiaAerea.creado.desc()).limit(10)
            
            result = await db.execute(query)
            guides = result.scalars().all()
            
            return [
                {
                    "numero": g.numero,
                    "observaciones": g.observaciones or "Sin observaciones detalladas.",
                    "fecha": g.creado.strftime("%H:%M")
                } for g in guides
            ]
        except Exception as e:
            logger.error(f"Error cargando detalle de observaciones: {e}")
            return []

    async def get_catalogo_entry(self, codigo: str) -> dict:
        """Busca un código en el catálogo y devuelve su nombre y descripción."""
        try:
            db = self.catalogo_repository.db
            query = select(Catalogo).where(Catalogo.codigo == codigo, Catalogo.habilitado == True)
            result = await db.execute(query)
            entry = result.scalars().first()
            if entry:
                return {
                    "codigo": entry.codigo,
                    "nombre": entry.nombre,
                    "descripcion": entry.descripcion,
                    "referencia": entry.referencia_codigo
                }
            return {"error": f"No se encontró información para el código '{codigo}'."}
        except Exception as e:
            logger.error(f"Error consultando catálogo por código: {e}")
            return {"error": f"Error interno al buscar el código '{codigo}'."}

    async def search_catalogo_by_reference(self, referencia_codigo: str) -> list[dict]:
        """Obtiene todos los elementos de una categoría."""
        try:
            entries = await self.catalogo_repository.load_by_referencia_nombre(referencia_codigo)
            return [
                {
                    "codigo": e.codigo,
                    "nombre": e.nombre,
                    "descripcion": e.descripcion
                } for e in entries
            ]
        except Exception as e:
            logger.error(f"Error buscando categoría en catálogo: {e}")
            return []
