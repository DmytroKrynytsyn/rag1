from pydantic import BaseModel

class EmbedRequest(BaseModel):
    text: str
    collection_name: str
