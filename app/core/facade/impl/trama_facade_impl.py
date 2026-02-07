
from utl.constantes import Catalogo
from app.configuration.facade.comun_facade import ComunFacade
from dto.trama_dtos import TramaComboResponse
from dto.trama_dtos import ManifiestoResponse
from dto.trama_dtos import ManifiestoFiltroRequest
from dto.trama_dtos import TramaFiltroRequest
from app.core.services.document_service import DocumentService
from dto.universal_dto import BaseOperacionResponse
from dto.trama_dtos import TramaRequest
from config.mapper import Mapper
from core.exceptions import AppBaseException
from dto.guia_aerea_dtos import GuiaAereaDataGridResponse
from dto.collection_response import CollectionResponse
from core.facade.facade_base import FacadeBase
from app.core.facade.trama_facade import TramaFacade
from app.core.services.trama_service import TramaService

from app.core.services.pdf_service import PDFService

class TramaFacadeImpl(TramaFacade, FacadeBase):

    def __init__(self, trama_service: TramaService, document_service: DocumentService, comun_facade: ComunFacade, pdf_service: PDFService):
        self.trama_service = trama_service
        self.document_service = document_service
        self.comun_facade = comun_facade
        self.pdf_service = pdf_service
    

    async def find(self, request: TramaFiltroRequest) -> CollectionResponse[GuiaAereaDataGridResponse]:
        data, total_count = await self.trama_service.find(request)
        elements = [Mapper.to_dto(x, GuiaAereaDataGridResponse) for x in data]
        
        return CollectionResponse[GuiaAereaDataGridResponse](
            elements=elements,
            totalCount=total_count,
            start=request.start,
            limit=request.limit
        )

    async def findTramas(self, t: ManifiestoFiltroRequest) -> CollectionResponse[ManifiestoResponse]:
        data, total_count = await self.trama_service.findTramas(t)
        manifiestos = [Mapper.to_dto(tt, ManifiestoResponse) for tt in data]

        return CollectionResponse[ManifiestoResponse](
            elements=manifiestos,
            totalCount=total_count,
            start=t.start,
            limit=t.limit
        )

    async def validarTrama(self, t: TramaRequest) -> BaseOperacionResponse:
        guias = []
        for id in t.guiaIds:
            guias.append(await self.document_service.get(id))
        await self.trama_service.validate_batch(guias)
        return BaseOperacionResponse(codigo=200, mensaje="Trama validada exitosamente")

    async def get_records_by_manifiesto_ids(self, ids: list[str]) -> list:
        return await self.trama_service.get_records_by_manifiesto_ids(ids)

    async def get_data_grid_records_by_ids(self, ids: list[str]) -> list:
        return await self.trama_service.get_data_grid_records_by_ids(ids)

    async def get_data_grid_records_by_manifiesto_id(self, manifiesto_id: str) -> list:
        return await self.trama_service.get_data_grid_records_by_manifiesto_id(manifiesto_id)

    def generate_flat_file_content(self, guias: list) -> str:
        return self.trama_service.generate_flat_file_content(guias)

    async def generate_manifest_pdf(self, guias: list) -> any:
        # Use PDF Service
        return self.pdf_service.generate_manifest(guias)

    async def generate_manifest_xml(self, guias: list) -> str:
        return await self.trama_service.generate_manifest_xml(guias)

    
    async def initFindTramas(self) -> TramaComboResponse:
        return TramaComboResponse(
            estado=await self.comun_facade.load_by_referencia_nombre(Catalogo.ESTADO_MANIFIESTO)
        )