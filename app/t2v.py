import requests
import os
from openai import OpenAI

API_KEY = os.environ["PZ_API_KEY"]

#FOLDER_ID = os.environ["YC_FOLDER_ID"]

# URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"

# headers = {
#     "Authorization": f"Api-Key {API_KEY}",
#     "Content-Type": "application/json",
# }

# def embed_doc(text: str):
#     body = {
#         "modelUri": f"emb://{FOLDER_ID}/text-embeddings-v2-doc/latest",
#         "text": text,
#         "dim": 768
#     }
    
#     response = requests.post(URL, headers=headers, json=body)

#     response.raise_for_status()

#     return response.json()["embedding"]


# def embed_query(text: str):
#     body = {
#         "modelUri": f"emb://{FOLDER_ID}/text-embeddings-v2-query/latest",
#         "text": text,
#         "dim": 768
#     }

#     response = requests.post(URL, headers=headers, json=body)

#     response.raise_for_status()

#     return response.json()["embedding"]


client = OpenAI(
  base_url="https://routerai.ru/api/v1",
  api_key=API_KEY,
)

def embed(text: str):
    response = client.embeddings.create(
        model="qwen/qwen3-embedding-4b",
        input=[text],
        dimensions=2560
    )
    return response.data[0].embedding