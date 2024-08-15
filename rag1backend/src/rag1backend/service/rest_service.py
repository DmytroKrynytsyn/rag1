from fastapi import APIRouter, HTTPException, Depends, Query
from rag1backend.repository.repository import VectorRepository
from app.schemas.text import TextRequest
from ..repository.repository import AbstractRepository, get_repository
import openai

router = APIRouter()

# Set your OpenAI API key
openai.api_key = 'your-openai-api-key'

# Dependency to get the repository, allowing for a custom collection name
def get_repository(collection_name: str = "text_embeddings") -> AbstractRepository:
    return VectorRepository(collection_name)

# Helper function to generate embedding using OpenAI
def get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response['data'][0]['embedding']
    return embedding

@router.post("/embed/")
async def embed_text(
    request: TextRequest, 
    repository: AbstractRepository = Depends(get_repository)
):
    try:
        # Generate embedding
        embedding = get_embedding(request.text)

        # Insert into Milvus
        repository.insert_text(embedding, request.text)
        return {"status": "success", "message": "Text embedded and stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
async def search_text(
    request: TextRequest, 
    repository: AbstractRepository = Depends(get_repository),
    limit: int = 5
):
    try:
        # Generate embedding for the query text
        query_embedding = get_embedding(request.text)

        # Perform search in Milvus
        results = repository.search_text(query_embedding, limit)
        
        # Extract and return the results
        matches = [
            {"id": result.id, "distance": result.distance, "text": result.entity.get("text")}
            for result in results[0]
        ]
        return {"status": "success", "matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
