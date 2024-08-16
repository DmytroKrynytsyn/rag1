from fastapi import APIRouter, HTTPException, Depends, Query
from rag1backend.model.embed_request import EmbedRequest
from rag1backend.model.search_request import SearchRequest
from rag1backend.repository.repository import VectorRepository
from ..repository.repository import get_repository
import openai
import os

router = APIRouter()

openai.api_key = os.getenv("OPEN_API_KEY")

def get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response['data'][0]['embedding']
    return embedding

@router.post("/embed/")
async def embed_text(
    request: EmbedRequest, 
    repository: VectorRepository = Depends(get_repository)):

    print("EmbedRequest: ", request.text)

    try:
        embedding = get_embedding(request.text)

        repository.insert_text(embedding, request.text)
        return {"status": "success", "message": "Text embedded and stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
async def search_text(
    request: SearchRequest, 
    repository: VectorRepository = Depends(get_repository),
    limit: int = 5):

    print("SearchRequest: ", request.text)

    try:
        query_embedding = get_embedding(request.text)
        results = repository.search_text(query_embedding, limit)
        
        matches = [
            {"id": result.id, "distance": result.distance, "text": result.entity.get("text")}
            for result in results[0]
        ]
        return {"status": "success", "matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
