from rag1backend.repository.milvus_repository import MilvusRepository
from rag1backend.repository.vector_repository import VectorRepository

def get_repository(collection_name: str) -> VectorRepository:
    return MilvusRepository(collection_name)