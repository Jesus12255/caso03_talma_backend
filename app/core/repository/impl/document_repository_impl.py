from sqlalchemy.ext.asyncio import AsyncSession
from app.core.domain.document import Document
from app.core.repository.document_repository import DocumentRepository
from sqlalchemy import select


class DocumentRepositoryImpl(DocumentRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, doc: Document) -> Document:
        print(f"DEBUG: Repository saving document {doc.file_name}")
        try:
            self.db.add(doc)
            print("DEBUG: Added to session")
            await self.db.commit()
            print("DEBUG: Committed")
            await self.db.refresh(doc)
            print("DEBUG: Refreshed")
            return doc
        except Exception as e:
            print(f"DEBUG: Error in repository save: {e}")
            raise e

    async def find_all(self) -> list[Document]:
        result = await self.db.execute(select(Document))
        return result.scalars().all()

    async def find_by_id(self, id):
        result = await self.db.execute(
            select(Document).where(Document.document_id == id)
        )
        return result.scalar_one_or_none()

    async def delete(self, id) -> bool:
        doc = await self.find_by_id(id)
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.commit()
        return True
