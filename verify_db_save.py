import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.core.domain.document import Document
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from config.database_config import DATABASE_URL
import uuid

async def verify_save():
    print("Starting verification v2...")
    # Create engine inside the loop to avoid loop mismatch errors
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = DocumentRepositoryImpl(session)
        doc = Document(
            document_id=uuid.uuid4(),
            type="verification_test",
            fields={"test": "value"},
            file_name="verify_test.pdf",
            is_anonymized=False
        )
        print(f"Attempting to save document: {doc.document_id}")
        try:
            saved_doc = await repo.save(doc)
            print(f"Save successful: {saved_doc.document_id}")
        except Exception as e:
            print(f"Save failed: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_save())
