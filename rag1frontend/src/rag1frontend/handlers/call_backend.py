import httpx
import os
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from ..utils.log import logger
import json


rag_backend_ip = os.getenv("RAG_BACKEND_IP")

kafka_connection_string = os.getenv("KAFKA_CONNECTION_STRING")
conf = { 'bootstrap.servers': kafka_connection_string }
producer = Producer(conf)

TOPIC_NAME = "rag1"
NUM_PARTITIONS = 3
REPLICATION_FACTOR = 2 

def delivery_report(err, msg):
    if err is not None:
        logger.info(f"Kafka message delivery failed: {err}")
    else:
        logger.info(f"Kafka message delivery to {msg.topic()} [{msg.partition()}] succeeded")

def create_topic_if_not_exists() -> None:
    admin_client = AdminClient(conf)
    existing_topics = admin_client.list_topics().topics

    if TOPIC_NAME not in existing_topics:
        logger.info(f"Kafka creating topic: {TOPIC_NAME}")
        new_topic = NewTopic(TOPIC_NAME, num_partitions=NUM_PARTITIONS, replication_factor=REPLICATION_FACTOR)
        admin_client.create_topics([new_topic])
    else:
        logger.info(f"Kafka topic {TOPIC_NAME} already exists.")

def embed(text: str, channel_name: str) -> None:
    try:
        logger.info(f"Embedding {len(text)} characters from {channel_name}")
        producer.produce(TOPIC_NAME, 
                         key=None, 
                         value=json.dumps({"text": text, "collection_name": channel_name}), 
                         callback=delivery_report)
        producer.flush()
    except httpx.RequestError as exc:
        logger.error(f'Exception calling embed backend {str(exc)}')

def search(question: str, channel_name: str, debug: bool) -> str | None:
    try:
        logger.info(f"Searching {question} in {channel_name}")
        rag_backend_url = f"http://{rag_backend_ip}/search/"

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                rag_backend_url,
                json={
                    "question": question,
                    "collection_name": channel_name,
                    "debug": "true" if debug else "false"
                }
            )

        if response.status_code == 200:
            return str(response.json())
        else:
            logger.error(f'Error calling search backend {response.status_code} {response.text}')

    except httpx.RequestError as exc:
        logger.error(f'Exception calling search backend {str(exc)}')

create_topic_if_not_exists()