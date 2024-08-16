from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections

from typing import List
import os

vector_db = os.getenv("VECTOR_DN_DNS_NAME")

class MilvusRepository:
    def __init__(self):
        connections.connect("default", host=vector_db, port="19530")
        print(f'Connected to {vector_db} vector db')

    def _get_or_create_collection(self, collection_name: str) -> Collection:
        if collection_name in Collection.list():
            return Collection(collection_name)
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, description=f"{collection_name} collection")
        collection = Collection(collection_name, schema)
        
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        return collection

    def insert_text(self, embedding: List[float], text: str, collection_name: str) -> None:

        collection = self._get_or_create_collection(collection_name)

        data = [
            [embedding],
            [text]
        ]
        collection.insert(data)

    def search_text(self, embedding: List[float], collection_name: str, limit: int = 5):
        collection = self._get_or_create_collection(collection_name)

        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = collection.search(
            data=[embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            expr=None
        )
        return results
