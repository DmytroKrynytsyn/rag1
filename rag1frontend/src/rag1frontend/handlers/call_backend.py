import httpx
import os

rag_backend_ip = os.getenv("RAG_BACKEND_IP")

def search(question: str, channel_name: str, debug: bool) -> str:
    try:
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
            return f'Error calling search backend {response.status_code} {response.text}'

    except httpx.RequestError as exc:
        return f'Exception calling search backend {str(exc)}'


def embed(text: str, user_name: str, datetime: int, channel_name: str) -> str:
    try:
        rag_backend_url = f"http://{rag_backend_ip}/embed/"

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                rag_backend_url,
                json={
                    "text": text,
                    "user_name": user_name, 
                    "datetime": datetime,
                    "collection_name": channel_name
                }
            )

        if response.status_code == 200:
            return str(response.json())
        else:
            return f'Error calling embed backend {response.status_code} {response.text}'

    except httpx.RequestError as exc:
        return f'Exception calling embed backend {str(exc)}'
