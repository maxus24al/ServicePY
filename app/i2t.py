import os
import json
import base64
import requests
from openai import OpenAI

YC_API_KEY = os.environ["YC_API_KEY"]
FOLDER_ID = os.environ["YC_FOLDER_ID"]

R_API_KEY = os.environ["API_KEY"]

client_y = OpenAI(
    api_key=YC_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=FOLDER_ID,
)

client_r = OpenAI(
    api_key=R_API_KEY,
    base_url="https://routerai.ru/api/v1"
)

def image_des(image_url: str, promt: str):
    response = requests.get(image_url, timeout=30)

    response.raise_for_status()


    mime = response.headers.get("Content-Type", "image/jpeg")
    image = base64.b64encode(response.content).decode("utf-8")


    response = client_y.chat.completions.create(
        model=f"gpt://{FOLDER_ID}/qwen3.6-35b-a3b/latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": promt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{image}"
                        },
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content

def image_ind(image_url: str):
    response = client_r.embeddings.create(
        model="voyageai/voyage-multimodal-3.5", 
        input=[
            {
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        dimensions=1024
    )
    
    return response.data[0].embedding