
from app.integration.service.embedding_service import EmbeddingService
import google.generativeai as genai
from config.config import settings

class EmbeddingServiceImpl(EmbeddingService):
    
    def __init__(self):
        genai.configure(api_key=settings.LLM_API_KEY)
        self.model = "models/gemini-embedding-001"

    async def get_embedding(self, text: str) -> list[float]:
        if not text:
            return []
            
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="RETRIEVAL_DOCUMENT",
                title="Embedding of identity"
            )
            return result['embedding']
        except Exception as e:
            # Fallback or log error
            print(f"Error generating embedding: {e}")
            return []
