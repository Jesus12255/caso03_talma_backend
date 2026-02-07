from dto.trama_dtos import TramaComboResponse
from dto.trama_dtos import ManifiestoFiltroRequest
from dto.trama_dtos import TramaFiltroRequest
from dto.trama_dtos import ManifiestoResponse
from dto.universal_dto import BaseOperacionResponse
from dto.trama_dtos import TramaRequest
from app.core.dependencies.dependencies_trama import get_trama_facade
from app.core.facade.trama_facade import TramaFacade
from app.core.dependencies.dependencies_documento import get_document_service
from dto.guia_aerea_dtos import GuiaAereaDataGridResponse
from dto.collection_response import CollectionResponse
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.services.document_service import DocumentService


router = APIRouter()


@router.post("/find", response_model=CollectionResponse[GuiaAereaDataGridResponse])
async def find(request: TramaFiltroRequest, trama_facade: TramaFacade = Depends(get_trama_facade)):
    return await trama_facade.find(request)

@router.get("/initFindTramas", response_model=TramaComboResponse)
async def initFindTramas(trama_facade: TramaFacade = Depends(get_trama_facade)):
    return await trama_facade.initFindTramas()

@router.post("/findTramas", response_model=CollectionResponse[ManifiestoResponse])
async def findTramas(request: ManifiestoFiltroRequest, trama_facade: TramaFacade = Depends(get_trama_facade)):
    return await trama_facade.findTramas(request)

@router.post("/validarTrama", response_model = BaseOperacionResponse)
async def validarTrama(request: TramaRequest,  trama_facade: TramaFacade = Depends(get_trama_facade)):
    return await trama_facade.validarTrama(request)   


@router.post("/generate/txt")
async def generate_txt(request: TramaRequest, document_service: DocumentService = Depends(get_document_service), trama_facade: TramaFacade = Depends(get_trama_facade)):
    guias = []
    
    if request.manifiestoIds:
        for mid in request.manifiestoIds:
             m_guias = await trama_facade.get_data_grid_records_by_manifiesto_id(str(mid))
             if m_guias:
                 guias.extend(m_guias)

    # Note: request.guiaIds was removed from DTO, so we only use manifiestoIds now.
        
    content = trama_facade.generate_flat_file_content(guias)
    
    return StreamingResponse(
        iter([content]),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=trama_generada.txt"}
    )

@router.post("/generate/pdf")
async def generate_pdf(request: TramaRequest, document_service: DocumentService = Depends(get_document_service), trama_facade: TramaFacade = Depends(get_trama_facade)):
    guias = []
    
    # User request: Only support manifiestoIds now for PDF
    if request.manifiestoIds:
        # Loop through manifiesto IDs (though typically just one for PDF)
        for mid in request.manifiestoIds:
             m_guias = await trama_facade.get_data_grid_records_by_manifiesto_id(str(mid))
             if m_guias:
                 guias.extend(m_guias)
        
    buffer = await trama_facade.generate_manifest_pdf(guias)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=manifiesto.pdf"}
    )

@router.post("/generate/xml")
async def generate_xml(request: TramaRequest, document_service: DocumentService = Depends(get_document_service), trama_facade: TramaFacade = Depends(get_trama_facade)):
    guias = []
    
    if request.manifiestoIds:
        for mid in request.manifiestoIds:
             m_guias = await trama_facade.get_data_grid_records_by_manifiesto_id(str(mid))
             if m_guias:
                 guias.extend(m_guias)
        
    content = await trama_facade.generate_manifest_xml(guias)
    
    return StreamingResponse(
        iter([content]),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=manifiesto_sunat.xml"}
    )
