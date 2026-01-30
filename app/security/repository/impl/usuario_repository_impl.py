import logging
from typing import List, Tuple
from sqlalchemy import func
from app.integration.impl.base_repository_impl import BaseRepositoryImpl
from app.security.domain import Usuario
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from app.security.domain.VwUsuario import VwUsuario
from app.security.repository.usuario_repository import UsuarioRepository
from core.exceptions import NotFoundException
from dto.collection_response import CollectionResponse
from dto.usuario_dtos import UsuarioFiltroRequest, UsuarioResponse

logger = logging.getLogger(__name__)

class UsuarioRepositoryImpl(BaseRepositoryImpl[Usuario], UsuarioRepository):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Usuario, db)


    async def save_or_update(self, t: Usuario) -> bool:
        try:
            resultado = await self.save(t)
            return resultado is not None
        except Exception as e: 
            logger.error(f"Error saving user: {e}", exc_info=True)
            return False
        



    async def  get(self, usuarioId:str) -> Usuario:
        try: 
            usuario = await self.get_by_id(usuarioId)
            if not usuario:
                raise NotFoundException("Usuario no encontrado")
            return usuario
        except Exception as e: 
            logger.error(f"Error getting user {usuarioId}: {e}", exc_info=True)
            raise NotFoundException("Usuario no encontrado")


    async def find(self, request: UsuarioFiltroRequest) -> Tuple[List[VwUsuario], int]:
        try:
            query = select(VwUsuario)
            
            # Existing filters
            if request.nombre:
                query = query.filter(VwUsuario.nombre_completo.ilike(f"%{request.nombre}%"))
            
            if request.rolCodigo:
                query = query.filter(VwUsuario.rol_codigo == request.rolCodigo)
                
            if request.fechaInicio and request.fechaFin:
                 query = query.filter(VwUsuario.fecha_consulta.between(request.fechaInicio, request.fechaFin))
            
            if request.habilitado is not None:
                query = query.filter(VwUsuario.habilitado == request.habilitado)
            
            # New Quick Search Filter (palabraClave)
            if request.palabraClave:
                search_term = f"%{request.palabraClave}%"
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        VwUsuario.nombre_completo.ilike(search_term),
                        VwUsuario.correo.ilike(search_term),
                        VwUsuario.documento.ilike(search_term)
                    )
                )
      
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await self.db.execute(count_query)
            total = total_count.scalar_one()

          
            query = query.order_by(VwUsuario.fecha_consulta.desc())
            query = query.offset(request.start).limit(request.limit)
            result = await self.db.execute(query)
            elements = result.scalars().all()

            return elements, total
            
        except Exception as e:
            logger.error(f"Error finding users: {e}", exc_info=True)
            return [], 0

    async def get_by_email(self, email: str) -> Usuario:
        try:
            query = select(Usuario).where(Usuario.correo == email, Usuario.habilitado == True)
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error validating email {email}: {e}", exc_info=True)
            return None
