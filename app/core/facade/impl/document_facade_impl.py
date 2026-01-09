import json
import logging
from typing import List
from uuid import UUID
from app.core.services.guia_aerea_interviniente_service import GuiaAereaIntervinienteService
from config.mapper import Mapper
from core.tasks.document_tasks import process_document_validations
from utl.file_util import FileUtil
from app.integration.service.storage_service import StorageService
from fastapi import Form, UploadFile
from fastapi.params import File
from fastapi.responses import StreamingResponse
from app.core.facade.document_facade import DocumentFacade
from app.core.services.document_service import DocumentService
from core.exceptions import AppBaseException
from dto.guia_aerea_dtos import DescargarGuiaAereaRequest, GuiaAereaComboResponse, GuiaAereaDataGridResponse, GuiaAereaFiltroRequest, GuiaAereaIntervinienteResponse, GuiaAereaRequest, GuiaAereaResponse, GuiaAereaSubsanarRequest
from dto.collection_response import CollectionResponse
from dto.universal_dto import BaseOperacionResponse
from utl.generic_util import GenericUtil



logger = logging.getLogger(__name__)

class DocumentFacadeImpl(DocumentFacade):

    def __init__(self, document_service: DocumentService, guia_aerea_interviniente_service: GuiaAereaIntervinienteService, storage_service: StorageService):
        self.document_service = document_service
        self.guia_aerea_interviniente_service = guia_aerea_interviniente_service
        self.storage_service = storage_service


    async def saveOrUpdate(self, files: List[UploadFile] = File(...), requestForm: str = Form(...)) -> BaseOperacionResponse:
        try:
            await self._validate_files(files)
            request = self.validate_request(requestForm)

            for tt in request:
                obj_req = GuiaAereaRequest.model_validate(tt)
                self.validar_campos_requeridos_guia_aerea(obj_req)
                await self.document_service.saveOrUpdate(obj_req)
                if obj_req.guiaAereaId:
                    process_document_validations.delay(obj_req.model_dump_json())
            return BaseOperacionResponse(codigo="200", mensaje="Documentos recibidos. Procesando en segundo plano.")
        
        except Exception as e:
            if isinstance(e, AppBaseException):
                raise e
            logger.error(f"Error al guardar documentos: {e}")
            raise AppBaseException(message=f"Error al procesar la solicitud: {e}")


    async def find(self, request: GuiaAereaFiltroRequest) -> CollectionResponse[GuiaAereaDataGridResponse]:
        data, total_count = await self.document_service.find(request)
        elements = [Mapper.to_dto(x, GuiaAereaDataGridResponse) for x in data]
        
        return CollectionResponse[GuiaAereaDataGridResponse](
            elements=elements,
            totalCount=total_count,
            start=request.start,
            limit=request.limit
        )

    async def reprocess(self, document_id: UUID) -> BaseOperacionResponse:
        process_document_validations.delay(str(document_id))
        return BaseOperacionResponse(codigo="200", mensaje="Reprocesando en segundo plano.")


    async def get(self, guia_aerea_id: UUID) -> GuiaAereaResponse:
        guia_aerea = await self.document_service.get(guia_aerea_id)
        guia_aerea_response = Mapper.to_dto(guia_aerea, GuiaAereaResponse)
        guia_aerea_intervinientes_response = []
        guia_aerea_intervinientes = await self.guia_aerea_interviniente_service.get_by_guia_aerea_id(guia_aerea_id)
        for interviniente in guia_aerea_intervinientes:
            guia_aerea_intervinientes_response.append(Mapper.to_dto(interviniente, GuiaAereaIntervinienteResponse))
        guia_aerea_response.intervinientesValidos = guia_aerea_intervinientes_response
        return guia_aerea_response


    async def updateAndReprocess(self, request: GuiaAereaSubsanarRequest) -> BaseOperacionResponse:
        await self.document_service.updateAndReprocess(request)
        return BaseOperacionResponse(codigo="200", mensaje="Guía aérea reprocesada correctamente.")


    def validar_campos_requeridos_guia_aerea(self, guia: GuiaAereaRequest):

        errores = []

        if not guia.numero or guia.numero.strip() == "":
            errores.append("El número de la guía aérea es obligatorio.")

        # Intervinientes
        if not guia.intervinientes or len(guia.intervinientes) != 2:
            errores.append("Debe incluir remitente y consignatario.")
        else:
            remitente = guia.intervinientes[0]
            consignatario = guia.intervinientes[1]

            if not remitente.nombre or not remitente.direccion:
                errores.append("Falta información del remitente.")

            if not consignatario.nombre or not consignatario.direccion:
                errores.append("Falta información del consignatario.")

        if not guia.origenCodigo:
            # errores.append("El aeropuerto de origen es obligatorio.")
            pass

        if not guia.destinoCodigo:
            # errores.append("El aeropuerto de destino es obligatorio.")
            pass

        if guia.cantidadPiezas is None or guia.cantidadPiezas < 1:
            errores.append("La cantidad de piezas debe ser mayor a cero.")

        if not guia.descripcionMercancia:
            # errores.append("La descripción de la mercadería es obligatoria.")
            pass

        if guia.pesoBruto is None or guia.pesoBruto <= 0:
            # errores.append("El peso bruto debe ser mayor a cero.")
            pass

        if not guia.tipoFleteCodigo:
            # errores.append("El tipo de flete es obligatorio.")
            pass

        if not guia.monedaCodigo:
            # errores.append("La moneda es obligatoria.")
            pass

        if guia.fechaEmision is None:
            # errores.append("La fecha de emisión de la guía es obligatoria.")
            pass

        if errores:
            raise AppBaseException(message=" ".join(errores))

    def validate_request(self, requestForm: str = Form(...)) -> List[GuiaAereaRequest]:
        try:
            request = json.loads(requestForm)
            
        except json.JSONDecodeError:
            raise AppBaseException(message="El formato del JSON no es válido")
            
        if GenericUtil.is_empty_list(request):
            raise AppBaseException(message="Debe de enviar al menos un documento en el request")

        return request

    async def _validate_files(self, files: List[UploadFile]):
        for file in files:
            await FileUtil.validate_file(file)

    async def init(self) -> GuiaAereaComboResponse:
        # TODO: Implement real logic. For now return empty or basic structure
        # If there are catalogs to load, call services here.
        return GuiaAereaComboResponse()


    async def descargarGuiaAerea(self, request: DescargarGuiaAereaRequest) -> StreamingResponse:
        if not request.url:
            raise AppBaseException(message="La URL del archivo es requerida.")
        
        stream_generator = self.storage_service.download_file_stream(request.url)
        
        filename = request.url.split("/")[-1] if request.url else "archivo"
        
        return StreamingResponse(
            stream_generator, 
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    async def delete(self, guia_aerea_id: UUID) -> BaseOperacionResponse:
        await self.document_service.delete(guia_aerea_id)
        return BaseOperacionResponse(codigo="200", mensaje="Registro eliminado correctamente.")


        