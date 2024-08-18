from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections, utility

from typing import List
import os

vector_db_ip = os.getenv("VECTOR_DB_IP")

class MilvusRepository:
    def __init__(self):
        connections.connect("default", host=vector_db_ip, port="19530")
        print(f'Connected to {vector_db_ip} vector db')

    def _get_or_create_collection(self, collection_name: str) -> Collection:
        if collection_name in utility.list_collections():
            return Collection(collection_name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="user_name", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="datetime", dtype=DataType.INT64)
        ]
        
        schema = CollectionSchema(fields, description=f"{collection_name} collection")
        
        collection = Collection(name=collection_name, schema=schema)
        
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        }
        
        collection.create_index(field_name="embedding", index_params=index_params)
        
        print(f"Collection {collection_name} created")
        
        return collection

    def insert_text(self, embedding: List[float], text: str, user_name: str, datetime: int, collection_name: str) -> None:

        collection = self._get_or_create_collection(collection_name)

        collection.insert([
            [None, embedding, text, user_name, datetime]
        ])

        collection.flush()

    def search_text(self, embedding: List[float], collection_name: str, limit: int = 5):
        collection = self._get_or_create_collection(collection_name)

        collection.load()

        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = collection.search(
            data=[embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["text", "user_name", "datetime"]
        )
        return results
