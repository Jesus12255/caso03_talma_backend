
from app.core.repository.perfil_riesgo_repository import PerfilRiesgoRepository
from app.core.domain.perfil_riesgo import PerfilRiesgo
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from sqlalchemy.orm import Session
from sqlalchemy import select
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