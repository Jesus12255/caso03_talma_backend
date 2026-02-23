
from app.core.repository.perfil_riesgo_repository import PerfilRiesgoRepository
from app.core.domain.perfil_riesgo import PerfilRiesgo
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class PerfilRiesgoRepositoryImpl(BaseRepositoryImpl[PerfilRiesgo], PerfilRiesgoRepository):

    def __init__(self, db: Session):
        super().__init__(PerfilRiesgo, db)

    async def find_by_vector_similarity(self, embedding: List[float], tipo: str, threshold: float = 0.1) -> Optional[PerfilRiesgo]:
        if not embedding:
            return None
        
        # Use select() for AsyncSession compatibility
        query = select(PerfilRiesgo).filter(
            PerfilRiesgo.tipo_interviniente_codigo == tipo,
            PerfilRiesgo.vector_identidad.isnot(None)
        ).order_by(
            PerfilRiesgo.vector_identidad.cosine_distance(embedding)
        ).filter(
            PerfilRiesgo.vector_identidad.cosine_distance(embedding) < threshold
        )
        
        try:
            logger.info(f"Ejecutando query de similitud vectorial para tipo: {tipo}")
            result = await self.db.execute(query)
            logger.info("Query ejecutado correctamente")
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error al ejecutar query de similitud: {e}")
            raise e

    async def find_dispersion_by_perfil(self, perfil_riesgo_id: str) -> dict:
        from app.core.domain.guia_aerea import GuiaAerea
        from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente
        
        perfil_query = select(PerfilRiesgo).filter(PerfilRiesgo.perfil_riesgo_id == perfil_riesgo_id)
        perfil_result = await self.db.execute(perfil_query)
        perfil = perfil_result.scalar_one_or_none()
        
        if not perfil:
            return {"pesoPromedio": 0.0, "pesoStdDev": 0.0, "puntos": []}
            
        nombres_busqueda = set(perfil.variaciones_nombre or [])
        if perfil.nombre_normalizado:
            nombres_busqueda.add(perfil.nombre_normalizado)
            
        guia_query = select(GuiaAerea.fecha_emision, GuiaAerea.peso_bruto).join(
            GuiaAereaInterviniente, GuiaAerea.guia_aerea_id == GuiaAereaInterviniente.guia_aerea_id
        ).filter(
            GuiaAereaInterviniente.nombre.in_(list(nombres_busqueda)),
            GuiaAereaInterviniente.rol_codigo == perfil.tipo_interviniente_codigo,
            GuiaAerea.peso_bruto.isnot(None),
            GuiaAerea.fecha_emision.isnot(None)
        ).order_by(GuiaAerea.fecha_emision)
        
        result = await self.db.execute(guia_query)
        puntos = [{"fecha": row.fecha_emision, "peso": float(row.peso_bruto)} for row in result.all()]
        
        return {
            "pesoPromedio": perfil.peso_promedio or 0.0,
            "pesoStdDev": perfil.peso_std_dev or 0.0,
            "puntos": puntos
        }