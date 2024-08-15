from abc import ABC, abstractmethod
from typing import List

from rag1backend.repository.milvus_repository import MilvusRepository

class VectorRepository(ABC):
    @abstractmethod
    def insert_text(self, embedding: List[float], text: str) -> None:
        pass

    @abstractmethod
    def search_text(self, embedding: List[float], limit: int = 5):
        pass

def get_repository(collection_name: str) -> VectorRepository:
    return MilvusRepository(collection_name)