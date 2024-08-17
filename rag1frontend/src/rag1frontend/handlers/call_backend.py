import httpx
import os

rag_backend_ip = os.getenv("RAG_BACKEND_IP")

def search(question: str, channel_name: str) -> str:
    try:
        rag_backend_url = f"http://{rag_backend_ip}/search/"

        with httpx.Client() as client:
            response = client.post(
                rag_backend_url,
                json={
                    "text": question,
                    "collection_name": channel_name
                },
                allow_redirects=True
            )

        if response.status_code == 200:
            return response.json() 
        else:
            return f'Error calling search backend {response.status_code} {response.text}'

    except httpx.RequestError as exc:
        return f'Exception calling search backend {str(exc)}'


def embed(text: str, channel_name: str) -> str:
    try:
        rag_backend_url = f"http://{rag_backend_ip}/embed/"

        with httpx.Client() as client:
            response = client.post(
                rag_backend_url,
                json={
                    "text": text,
                    "collection_name": channel_name
                },
                allow_redirects=True
            )

        if response.status_code == 200:
            return response.json() 
        else:
            return f'Error calling embed backend {response.status_code} {response.text}'

    except httpx.RequestError as exc:
        return f'Exception calling embed backend {str(exc)}'
