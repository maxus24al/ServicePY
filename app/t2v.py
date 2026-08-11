import requests
import os

API_KEY = os.environ["YC_API_KEY"]
FOLDER_ID = os.environ["YC_FOLDER_ID"]

URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"

headers = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "application/json",
}

def embed_doc(text: str):
    body = {
        "modelUri": f"emb://{FOLDER_ID}/text-embeddings-v2-doc/latest",
        "text": text,
    }
    
    response = requests.post(URL, headers=headers, json=body)

    response.raise_for_status()
    return response.json()["embedding"]


def embed_query(text: str):
    body = {
        "modelUri": f"emb://{FOLDER_ID}/text-embeddings-v2-query/latest",
        "text": text,
    }

    response = requests.post(URL, headers=headers, json=body)

    response.raise_for_status()
    return response.json()["embedding"]

