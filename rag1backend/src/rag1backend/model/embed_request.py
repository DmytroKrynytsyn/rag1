from pydantic import BaseModel

class EmbedRequest(BaseModel):
    text: str
    user_name: str
    datetime: int
    collection_name: str
