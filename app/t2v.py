import requests
import os
from openai import OpenAI
import re
import pymorphy3


API_KEY = os.environ["API_KEY"]
YC_API_KEY = os.environ["YC_API_KEY"]
FOLDER_ID = os.environ["YC_FOLDER_ID"]
EMBEDDER = os.getenv("EMBED_PROVIDER", "yandexai")

URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"

headers = {
    "Authorization": f"Api-Key {YC_API_KEY}",
    "Content-Type": "application/json",
}

def embed_doc(text: str):
    if EMBEDDER == "routerai":
      return embed(text)
      
    body = {
        "modelUri": f"emb://{FOLDER_ID}/text-embeddings-v2-doc/latest",
        "text": text,
        "dim": 768
    }
    
    response = requests.post(URL, headers=headers, json=body)

    response.raise_for_status()

    return response.json()["embedding"]


def embed_query(text: str):
    if EMBEDDER == "routerai":
      return embed(text)
      

    body = {
        "modelUri": f"emb://{FOLDER_ID}/text-embeddings-v2-query/latest",
        "text": text,
        "dim": 768
    }

    response = requests.post(URL, headers=headers, json=body)

    response.raise_for_status()

    return response.json()["embedding"]


client = OpenAI(
  base_url="https://routerai.ru/api/v1",
  api_key=API_KEY,
)

morph = pymorphy3.MorphAnalyzer()

def embed(text: str):
    response = client.embeddings.create(
        model="qwen/qwen3-embedding-4b",
        input=[text],
        dimensions=2560
    )
    return response.data[0].embedding


def lemmatize(text: str) -> str:
    words = re.findall(r'[а-яА-ЯёЁa-zA-Z0-9]+', text.lower())

    lemmas = []
    for word in words:
        if re.match(r'^[а-яА-ЯёЁ]+$', word):
            lemmas.append(morph.parse(word)[0].normal_form)
        else:
            lemmas.append(word)
    return "".join(lemmas)


