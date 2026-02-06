from dto.trama_dtos import TramaComboResponse
from dto.trama_dtos import ManifiestoResponse
from dto.trama_dtos import TramaFiltroRequest
from dto.trama_dtos import ManifiestoFiltroRequest
from dto.universal_dto import BaseOperacionResponse
from dto.trama_dtos import TramaRequest
from abc import ABC, abstractmethod
from dto.collection_response import CollectionResponse
from dto.guia_aerea_dtos import GuiaAereaDataGridResponse

class TramaFacade(ABC):

    @abstractmethod
    async def find(self, request: TramaFiltroRequest) -> CollectionResponse[GuiaAereaDataGridResponse]:
        pass

    @abstractmethod
    async def validarTrama(self, request: TramaRequest) -> BaseOperacionResponse:
        pass

    @abstractmethod
    async def findTramas(self, request: ManifiestoFiltroRequest) -> CollectionResponse[ManifiestoResponse]:
        pass

    @abstractmethod
    async def get_records_by_manifiesto_ids(self, ids: list[str]) -> list:
        pass

    @abstractmethod
    def generate_flat_file_content(self, guias: list) -> str:
        pass

    @abstractmethod
    async def generate_manifest_pdf(self, guias: list) -> any:
        pass

    @abstractmethod
    async def generate_manifest_xml(self, guias: list) -> str:
        pass

    @abstractmethod
    async def initFindTramas(self) -> TramaComboResponse:
        pass

    @abstractmethod
    async def get_data_grid_records_by_ids(self, ids: list[str]) -> list:
        pass

    @abstractmethod
    async def get_data_grid_records_by_manifiesto_id(self, manifiesto_id: str) -> list:
        pass