from pydantic import BaseModel

class SearchRequest(BaseModel):
    question: str
    collection_name: str
    debug: str
