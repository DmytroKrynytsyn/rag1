from abc import ABC, abstractmethod
from typing import List

class VectorRepository(ABC):
    @abstractmethod
    def insert_text(self, embedding: List[float], text: str) -> None:
        pass

    @abstractmethod
    def search_text(self, embedding: List[float], limit: int = 5):
        pass