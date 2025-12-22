
import asyncio
import fitz
from typing import AsyncGenerator
from app.core.services.impl.analyze_service_impl import AnalyzeServiceImpl
from app.integration.extraction_engine import ExtractionEngine

class MockExtractionEngine(ExtractionEngine):
    async def extract_stream(self, base64_images: list[str]) -> AsyncGenerator[str, None]:
        print(f"Mock Engine received {len(base64_images)} images.")
        if len(base64_images) != 2:
             print("ERROR: Expected 2 images!")
        else:
             print("SUCCESS: Received correct number of images.")
        
        yield "token_batch_1"
        yield "token_batch_2"

    async def extract_data_from_image(self, base64_image: str) -> dict:
        return {"mock": "data"}

async def test_batch_flow():
    engine = MockExtractionEngine()
    service = AnalyzeServiceImpl(engine)
    
    # Create two dummy PDFs, 1 page each
    doc1 = fitz.open()
    doc1.new_page().insert_text((10, 10), "Doc1")
    pdf1 = doc1.tobytes()
    doc1.close()

    doc2 = fitz.open()
    doc2.new_page().insert_text((10, 10), "Doc2")
    pdf2 = doc2.tobytes()
    doc2.close()

    files_data = [
        {"filename": "doc1.pdf", "content": pdf1},
        {"filename": "doc2.pdf", "content": pdf2}
    ]

    print("Starting batch stream test...")
    async for item in service.upload_stream(files_data):
        print(f"Stream output: {item.strip()}")
    print("Batch stream test finished.")

if __name__ == "__main__":
    asyncio.run(test_batch_flow())
