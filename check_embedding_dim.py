import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY")
if not api_key:
    print("Error: LLM_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    model_name = "models/gemini-embedding-001"
    try:
        print(f"Generating embedding with {model_name}...")
        result = genai.embed_content(
            model=model_name,
            content="Hello world",
            task_type="RETRIEVAL_DOCUMENT",
            title="Embedding of identity"
        )
        embedding = result['embedding']
        print(f"Embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"Error generating embedding: {e}")
