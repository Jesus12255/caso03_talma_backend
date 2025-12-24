from app.security.domain import Usuario
from app.security.repository.usuario_repository import UsuarioRepository
from app.security.service.usuario_service import UsuarioService
from config.mapper import Mapper
from dto.universal_dto import BaseOperacionResponse
from dto.usuario_dtos import UsuarioRequest, UsuarioFiltroRequest, UsuarioFiltroResponse
from dto.collection_response import CollectionResponse
from utl.generic_util import GenericUtil
from config.config import settings
from utl.security_util import SecurityUtil

class UsuarioServiceImpl(UsuarioService):

    def __init__(self, usuario_repository: UsuarioRepository, modelMapper: Mapper):
        self.usuario_repository = usuario_repository
        self.modelMapper = modelMapper

    async def saveOrUpdate(self, t: UsuarioRequest) -> None:

        if GenericUtil.no_es_nulo(t, "usuarioId"):
            usuario = await self.usuario_repository.get(t.usuarioId)
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
            await self.usuario_repository.save(usuario)

        else:
            usuario = self.modelMapper.to_entity(t, Usuario)
            usuario.usuario = t.primerNombre + t.apellidoPaterno + GenericUtil.generate_unique_code_8()
            usuario.password = SecurityUtil.get_password_hash(settings.PASWORD_INICIAL) 
            await self.usuario_repository.save(usuario)
            


    async def get(self, usuarioId: str) -> Usuario:
        return await self.usuario_repository.get(usuarioId)

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

















    