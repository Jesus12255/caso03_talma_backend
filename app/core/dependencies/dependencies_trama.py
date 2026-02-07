from app.configuration.dependencies.dependencies_catalogo import get_comun_facade
from app.core.dependencies.dependencies_documento import get_document_service
from app.core.facade.impl.trama_facade_impl import TramaFacadeImpl
from app.core.services.impl.trama_service_impl import TramaServiceImpl
from app.core.dependencies.dependencies_documento import get_guia_aerea_filtro_repository
from fastapi import Depends
from app.core.dependencies.dependencies_manifiesto import get_manifiesto_repository

from app.core.services.pdf_service import PDFService

def get_pdf_service():
    return PDFService()

def get_trama_service(guia_aerea_filtro_repository = Depends(get_guia_aerea_filtro_repository), manifiesto_repository = Depends(get_manifiesto_repository)):
    return TramaServiceImpl(guia_aerea_filtro_repository, manifiesto_repository)

def get_trama_facade(trama_service = Depends(get_trama_service), document_service = Depends(get_document_service), comun_facade = Depends(get_comun_facade), pdf_service = Depends(get_pdf_service)):
    return TramaFacadeImpl(trama_service, document_service, comun_facade, pdf_service)