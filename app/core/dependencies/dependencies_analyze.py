from functools import lru_cache

from fastapi import Depends
from app.core.facade.document_facade import DocumentFacade
from app.core.facade.impl.analyze_facade_impl import AnalyzeFacadeImpl
from app.core.services.analyze_service import AnalyzeService
from app.core.services.impl.analyze_service_impl import AnalyzeServiceImpl
from app.integration.extraction_engine import ExtractionEngine
from app.integration.impl.extraction_engine_impl import ExtractionEngineImpl


from app.core.services.document_service import DocumentService
from app.core.dependencies.dependencies_documento import get_document_facade, get_document_service

def get_extraction_engine() -> ExtractionEngine:
    return ExtractionEngineImpl()

def get_analyze_service(document_service: DocumentService = Depends(get_document_service), document_facade: DocumentFacade = Depends(get_document_facade)) -> AnalyzeService:
    engine = get_extraction_engine()
    return AnalyzeServiceImpl(extraction_engine=engine, document_service=document_service, document_facade=document_facade )

def get_analyze_facade(service = Depends(get_analyze_service)):
    return AnalyzeFacadeImpl(service)



