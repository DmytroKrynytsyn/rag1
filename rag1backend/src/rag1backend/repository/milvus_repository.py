from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections
from rag1backend.repository.repository import VectorRepository

from typing import List
import os

vector_db = os.getenv("VECTOR_DN_DNS_NAME")

class MilvusRepository(VectorRepository):
    def __init__(self, collection_name):
        connections.connect("default", host=vector_db, port="19530")
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self) -> Collection:
        if self.collection_name in Collection.list():
            return Collection(self.collection_name)
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, description=f"{self.collection_name} collection")
        collection = Collection(self.collection_name, schema)
        
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        return collection

    def insert_text(self, embedding: List[float], text: str) -> None:
        data = [
            [embedding],
            [text]
        ]
        self.collection.insert(data)

    def search_text(self, embedding: List[float], limit: int = 5):
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            expr=None
        )
        return results
