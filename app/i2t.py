import os
import base64
import requests
from openai import OpenAI

API_KEY = os.environ["YC_API_KEY"]
FOLDER_ID = os.environ["YC_FOLDER_ID"]

client = OpenAI(
    api_key=API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=FOLDER_ID,
)

def image_des(image_url: str):
    response = requests.get(image_url, timeout=30)

    response.raise_for_status()


    mime = response.headers.get("Content-Type", "image/jpeg")
    image = base64.b64encode(response.content).decode("utf-8")


    response = client.chat.completions.create(
        model=f"gpt://{FOLDER_ID}/qwen3.6-35b-a3b/latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Опиши только один главный предмет мебели с максимальным "
                            "количеством объективных признаков. Используй обычный связный "
                            "текст. Не упоминай ничего, кроме этого предмета. "
                            "Обязательно опиши форму, цвет, материал, конструкцию, "
                            "обивку, ножки, подлокотники, спинку, фактуру и другие "
                            "видимые особенности."
                        ),
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