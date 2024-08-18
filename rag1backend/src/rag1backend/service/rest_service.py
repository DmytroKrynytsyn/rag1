from fastapi import APIRouter, HTTPException
from rag1backend.model.embed_request import EmbedRequest
from rag1backend.model.search_request import SearchRequest
from langchain.text_splitter import RecursiveCharacterTextSplitter

import openai
import os

from rag1backend.repository.milvus_repository import MilvusRepository

router = APIRouter(redirect_slashes=False)
repository: MilvusRepository = MilvusRepository()

openai.api_key = os.getenv("OPEN_API_KEY")

def get_embedding(text: str):
    # Use the new `openai.embeddings.create` method
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    # Access the embedding data using dot notation
    embedding = response.data[0].embedding
    return embedding

def semantic_chunker(text: str, chunk_size: int = 1000, overlap_ratio: float = 0.2) -> List[str]:
    # Define chunk size and overlap
    overlap_size = int(chunk_size * overlap_ratio)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap_size,
        separators=["\n"]
    )

    chunks = text_splitter.split_text(text)
    return chunks

@router.post("/embed/")
def embed_text(request: EmbedRequest):

    print(f"EmbedRequest, text{request.text[:10]}, collection {request.collection_name}")

    try:
        chunks = semantic_chunker(request.text, chunk_size=1000, overlap_ratio=0.2)
        for chunk in chunks:
            embedding = get_embedding(chunk)
            repository.insert_text(embedding, chunk, request.user_name, request.timestamp, request.collection_name)

        return {"status": "success", "message": f"Text embedded, {len(chunks)} chunks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
def search_text(request: SearchRequest, limit: int = 5):

    print(f"SearchRequest, text{request.text[:10]}, collection {request.collection_name}")

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
