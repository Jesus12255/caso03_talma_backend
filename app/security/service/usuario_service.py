from abc import ABC, abstractmethod

from app.security.domain import Usuario
from dto.universal_dto import BaseOperacionResponse
from dto.usuario_dtos import UsuarioRequest, UsuarioFiltroRequest, UsuarioFiltroResponse
from dto.collection_response import CollectionResponse


class UsuarioService(ABC):
    
    @abstractmethod
    async def saveOrUpdate(self, request: UsuarioRequest) -> None:
        pass

    @abstractmethod
    async def get(self, usuarioId: str) -> Usuario:
        pass

    @abstractmethod
    async def find(self, request: UsuarioFiltroRequest) -> CollectionResponse[UsuarioFiltroResponse]:
        pass
