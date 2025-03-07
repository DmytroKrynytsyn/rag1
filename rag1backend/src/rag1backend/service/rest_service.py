
from fastapi import APIRouter, HTTPException
from rag1backend.model.embed_request import EmbedRequest
from rag1backend.model.search_request import SearchRequest
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from aiokafka import AIOKafkaConsumer
import asyncio

import openai
import os

from ..utils.log import logger


from rag1backend.repository.milvus_repository import MilvusRepository

router = APIRouter(redirect_slashes=False)
repository: MilvusRepository = MilvusRepository()

openai.api_key = os.getenv("OPEN_API_KEY")

TOPIC_NAME = "rag1"
kafka_connection_string = os.getenv("KAFKA_CONNECTION_STRING")

topic_exists = False

async def wait_for_topic(consumer):
    global topic_exists

    if topic_exists:
        return

    while True:
        try:
            metadata = await consumer.topics()
            if TOPIC_NAME in metadata:
                topic_exists = True
                logger.info(f"Topic {TOPIC_NAME} is now available.")
                return
            logger.info(f"Waiting for topic {TOPIC_NAME} to be created...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error checking topic: {e}")
            await asyncio.sleep(5)

async def consume():
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        loop=asyncio.get_running_loop(),
        bootstrap_servers=kafka_connection_string,
        group_id="rag1",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    await wait_for_topic(consumer)

    try:
        async for msg in consumer:
            logger.info(f"Received message: {len(msg.value)} bytes")
    finally:
        await consumer.stop()


@router.on_event("startup")
async def start_kafka_consumer():
    asyncio.create_task(consume())


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

    logger.info(f"EmbedRequest, text '{request.text[:10]} ...', collection {request.collection_name}, user {request.user_name}")

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
def search_text(request: SearchRequest):
    logger.info(f"SearchRequest, text {request.question[:10]}, collection {request.collection_name}")

    try:
        query_embedding = get_embedding(request.question)
        results = repository.search_text(query_embedding, request.collection_name)

        logger.info(f"results = {str(results)}")
        
        matches = [
            {"id": result.id, "distance": result.distance, "text": result.entity.get("text")}
            for result in results[0]
        ]

        prompt = prepare_openai_prompt(matches, request.question)

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}"},
            ]
        )

        logger.info(f"response = {str(response)}")

        summary = response.choices[0].message.content

        return {"status": "success", "summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
