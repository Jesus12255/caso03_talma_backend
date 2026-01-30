from app.security.domain import Usuario
from core.exceptions import  AppBaseException, NotFoundException
from fastapi import status
from app.security.repository.usuario_repository import UsuarioRepository
from app.security.service.usuario_service import UsuarioService
from config.mapper import Mapper
from core.facade.facade_base import FacadeBase
from dto.universal_dto import BaseOperacionResponse
from dto.usuario_dtos import UsuarioCambioPasswordRequest, UsuarioRequest, UsuarioFiltroRequest, UsuarioFiltroResponse, UsuarioStatusRequest
from dto.collection_response import CollectionResponse
from utl.generic_util import DateUtil, GenericUtil
from config.config import settings
from utl.security_util import SecurityUtil

from app.core.services.email_service import EmailService

import asyncio

class UsuarioServiceImpl(UsuarioService, FacadeBase):

    def __init__(self, usuario_repository: UsuarioRepository, modelMapper: Mapper, email_service: EmailService):
        self.usuario_repository = usuario_repository
        self.modelMapper = modelMapper
        self.email_service = email_service

    async def saveOrUpdate(self, t: UsuarioRequest) -> None:

        if GenericUtil.no_es_nulo(t, "usuarioId"):
            usuario = await self.get(t.usuarioId)
            if t.rolId: 
                usuario.rol_id = t.rolId
            usuario.primer_nombre = t.primerNombre
            usuario.segundo_nombre = t.segundoNombre
            usuario.apellido_paterno = t.apellidoPaterno
            usuario.apellido_materno = t.apellidoMaterno
            usuario.tipo_documento_codigo = t.tipoDocumentoCodigo
            usuario.documento = t.documento
            usuario.correo = t.correo
            usuario.celular = t.celular
            usuario.modificado = DateUtil.get_current_local_datetime()
            usuario.modificado_por = self.session.full_name
            await self.usuario_repository.save(usuario)

        else:
            await self.validate_email(t.correo)
            usuario = self.modelMapper.to_entity(t, Usuario)
            usuario.usuario = t.primerNombre + t.apellidoPaterno + GenericUtil.generate_unique_code_4()
            raw_password = settings.PASWORD_INICIAL
            usuario.password = SecurityUtil.get_password_hash(raw_password) 
            
            usuario.creado = DateUtil.get_current_local_datetime()
            usuario.creado_por = self.session.full_name
            
            await self.usuario_repository.save(usuario)
            
            if usuario.correo:
                nombre_completo = f"{usuario.primer_nombre} {usuario.apellido_paterno}"
                asyncio.create_task(
                    asyncio.to_thread(
                        self.email_service.send_credentials_email, 
                        usuario.correo, 
                        usuario.usuario, 
                        raw_password, 
                        nombre_completo
                    )
                )


    async def validate_email(self, email: str) -> bool:
        usuario = await self.usuario_repository.get_by_email(email)
        if usuario: 
            raise AppBaseException(message=f"El correo ya se encuentra registrado, le pertenece al usuario {usuario.usuario}", status_code=status.HTTP_400_BAD_REQUEST)
      
            
    async def changeStatus(self, t: UsuarioStatusRequest) -> None:
        usuario = await self.usuario_repository.get(t.usuarioId)
        if usuario:
            usuario.habilitado = t.habilitado
            await self.usuario_repository.save(usuario)

    async def get(self, usuarioId: str) -> Usuario:
        usuario = await self.usuario_repository.get(usuarioId)
        if not usuario:
             raise NotFoundException("El usuario no se encuentra registrado", status_code=status.HTTP_404_NOT_FOUND)
        return usuario

    async def find(self, request: UsuarioFiltroRequest) -> CollectionResponse[UsuarioFiltroResponse]:
        usuarios, count = await self.usuario_repository.find(request)
        datos = []
        for u in usuarios:
            datos.append(UsuarioFiltroResponse(
                usuarioId=str(u.usuario_id),
                nombreCompleto=u.nombre_completo,
                correo=u.correo,
                celular=u.celular,
                rolCodigo=u.rol_codigo,
                rol=u.rol,
                tipoDocumento=u.tipo_documento,
                documento=u.documento,
                estado='ACTIVO' if u.habilitado else 'INACTIVO',
                creado=str(u.fecha_consulta) if u.fecha_consulta else None
            ))
        return CollectionResponse[UsuarioFiltroResponse](
            elements=datos, 
            totalCount=count,
            start=request.start,
            limit=request.limit,
            sort=request.sort
        )

    async def updatePassword(self, request: UsuarioCambioPasswordRequest) -> BaseOperacionResponse:
        usuario = await self.get(self.session.user_id)
        if SecurityUtil.verify_password(request.password, usuario.password):
            raise AppBaseException(message="La nueva contraseña no puede ser igual a la anterior", status_code=status.HTTP_400_BAD_REQUEST)
        usuario.password = SecurityUtil.get_password_hash(request.password)
        usuario.modificado = DateUtil.get_current_local_datetime()
        usuario.modificado_por = self.session.full_name
        await self.usuario_repository.save(usuario)















    