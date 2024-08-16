from fastapi import APIRouter, HTTPException, Depends, Query
from rag1backend.model.embed_request import EmbedRequest
from rag1backend.model.search_request import SearchRequest

import openai
import os

from rag1backend.repository.milvus_repository import MilvusRepository

router = APIRouter()
repository: MilvusRepository = MilvusRepository()

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
    request: EmbedRequest):

    print("EmbedRequest: ", request.text)

    try:
        embedding = get_embedding(request.text)

        repository.insert_text(embedding, request.text, request.collection_name)
        return {"status": "success", "message": "Text embedded and stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
async def search_text(
    request: SearchRequest, 
    limit: int = 5):

    print("SearchRequest: ", request.text)

    try:
        query_embedding = get_embedding(request.text)
        results = repository.search_text(query_embedding, request.collection_name, limit)
        
        matches = [
            {"id": result.id, "distance": result.distance, "text": result.entity.get("text")}
            for result in results[0]
        ]
        return {"status": "success", "matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
