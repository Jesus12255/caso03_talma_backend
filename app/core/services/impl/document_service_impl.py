
from app.core.domain.document import Document
from app.core.repository.document_repository import DocumentRepository
from app.core.services.document_service import DocumentService
from config.mapper import Mapper
from dto.document import DocumentRequest



class DocumentServiceImpl(DocumentService):

    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    async def save(self, t: DocumentRequest):
        document = Mapper.to_entity(t, Document)
        document.fields = [field.model_dump() for field in t.fields]
        document.type = t.detectedType   
        document.file_name = t.fileName
        document.is_anonymized = t.isAnonymized 
        await self.document_repository.save(document)
