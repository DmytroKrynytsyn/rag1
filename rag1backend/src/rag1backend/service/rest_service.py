
from fastapi import APIRouter, HTTPException
from rag1backend.model.embed_request import EmbedRequest
from rag1backend.model.search_request import SearchRequest
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Optional, Union

import openai
import os

from rag1backend.repository.milvus_repository import MilvusRepository

router = APIRouter(redirect_slashes=False)
repository: MilvusRepository = MilvusRepository()

openai.api_key = os.getenv("OPEN_API_KEY")

def prepare_openai_prompt(results: List[dict], question: str) -> str:

    top_matches = sorted(results, key=lambda x: x['distance'])[:3]
    
    prompt = f"Please summarize the following answers, in one answer on question '{question}', as a text of 3-5 sentences long:\n\n"
    for idx, match in enumerate(top_matches):
        prompt += f"Match {idx + 1}:\nText: {match['text']}\n\n"
    
    return prompt

def get_embedding(text: str):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )

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
    print(f"EmbedRequest, text '{request.text[:10]} ...', collection {request.collection_name}, user {request.user_name}")

    try:
        chunks = semantic_chunker(request.text, chunk_size=1000, overlap_ratio=0.2)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        for chunk in chunks:
            embedding = get_embedding(chunk)
            repository.insert_text(embedding, chunk, request.user_name, request.datetime, request.collection_name)

        return {"status": "success", "message": f"Text embedded, {len(chunks)} chunks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
def search_text(request: SearchRequest, limit: int = 5):
    print(f"SearchRequest, text {request.question[:10]}, collection {request.collection_name}")

    try:
        query_embedding = get_embedding(request.question)
        results = repository.search_text(query_embedding, request.collection_name, limit)

        print(f"results = {str(results)}")
        
        matches = [
            {"id": result.id, "distance": result.distance, "text": result.entity.get("text")}
            for result in results[0]
        ]

        prompt = prepare_openai_prompt(matches, request.question)

        model: str = "gpt-3.5-turbo",
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.5,
        max_tokens: int = 256,
        n: int = 1,
        stop: Optional[Union[str, list]] = None,
        presence_penalty: float = 0,
        frequency_penalty: float = 0.1,
        
        messages = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": prompt},
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )

        print(f"response = {str(response)}")
        
        summary = response['choices'][0]['text'].strip()

        return {"status": "success", "matches": matches, "summary": summary} if request.debug == "true" else {"status": "success", "summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
