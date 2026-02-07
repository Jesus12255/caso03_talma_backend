from app.configuration.facade.comun_facade import ComunFacade
from app.security.domain import Usuario
from app.security.facade.usuario_facade import UsuarioFacade
from app.security.service.usuario_service import UsuarioService
from config.mapper import Mapper
from core.exceptions import AppBaseException
from dto.universal_dto import BaseOperacionResponse, ComboBaseResponse
from dto.usuario_dtos import UsuarioCambioPasswordRequest, UsuarioComboResponse, UsuarioRequest, UsuarioResponse, UsuarioFiltroRequest, UsuarioFiltroResponse, UsuarioStatusRequest
from dto.collection_response import CollectionResponse
from dto.menu_dtos import MenuResponse
from utl.generic_util import Constantes


class UsuarioFacadeImpl(UsuarioFacade):

    def __init__(self, usuario_service: UsuarioService, modelMapper: Mapper, comun_facade: ComunFacade):
        self.usuario_service = usuario_service
        self.modelMapper = modelMapper
        self.comun_facade = comun_facade
    
    async def saveOrUpdate(self, t: UsuarioRequest) -> BaseOperacionResponse:
        await self.usuario_service.saveOrUpdate(t)
        return BaseOperacionResponse(codigo="200", mensaje="Documentos guardados correctamente")


    async def get(self, usuarioId: str) -> UsuarioResponse:
        usuario = await self.usuario_service.get(usuarioId)
        usuarioResponse  = self.modelMapper.to_dto(usuario, UsuarioResponse)
        combo = UsuarioComboResponse()
        combo.tipoDocumento = await self.comun_facade.load_by_referencia_nombre(Constantes.TIPO_DOCUMENTO)
        combo.rol = await self.comun_facade.load_rol()
        usuarioResponse.combo = combo
        return  usuarioResponse

    async def find(self, request: UsuarioFiltroRequest) -> CollectionResponse[UsuarioFiltroResponse]:
        return await self.usuario_service.find(request)
    
    async def changeStatus(self, t: UsuarioStatusRequest) -> BaseOperacionResponse:
        await self.usuario_service.changeStatus(t)
        return BaseOperacionResponse(codigo="200", mensaje="Estado actualizado correctamente")

    async def init(self) -> UsuarioComboResponse:
        comboResponse = UsuarioComboResponse()
        comboResponse.rol = await self.comun_facade.load_rol()
        return comboResponse;

    async def initForm(self) -> UsuarioComboResponse:
        comboResponse = UsuarioComboResponse()
        comboResponse.tipoDocumento = await self.comun_facade.load_by_referencia_nombre(Constantes.TIPO_DOCUMENTO)
        comboResponse.rol = await self.comun_facade.load_rol()
        return comboResponse;


    async def updatePassword(self, request: UsuarioCambioPasswordRequest) -> BaseOperacionResponse:
        if request.password != request.confirmarPassword:
            return AppBaseException(codigo="400", mensaje="Las contraseñas no coinciden")
        await self.usuario_service.updatePassword(request)
        return BaseOperacionResponse(codigo="200", mensaje="Se cambió la contraseña correctamente")

    async def loadMenu(self) -> MenuResponse:
        return await self.usuario_service.load_menu()