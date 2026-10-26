Авторизация:
 В header запроса прописать
 'Authorization': 'Bearer API_TOKEN'

POST /product
Запрос:
{
    "id": id,
    "name": name,
    "type": type,
    "description": description,
    "image_t": url,
    "image_ind": url,
    "promt": ""
}

image_t - url для создания текста
image_ind - url для индексации картинки
ОДНОВРЕМЕННО НЕ РАБОТАЕТ!

Ответ:
{
    "id": id,
    "name": name,
    "type": string,
    "description": description,
    "image_t": string,
    "image_t_url": url,
    "image_ind_url": url,
    "promt": promt
}

POST /product/image
Запрос:
{
    "id": id,
    "image": url,
    "promt": string
}

Ответ:
{
    "id": id,
    "image": string,
    "image_url": url,
    "promt": string
}

POST /products
Запрос:
[
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": url,
        "promt": string
    },
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": url,
        "promt": string
    }
]

Ответ:
[
    {
        "id": id,
        "name": name,
        "type": string,
        "description": description,
        "image": string,
        "image_url": url,
        "promt": promt
    },
    {
        "id": id,
        "name": name,
        "type": string,
        "description": description,
        "image": image,
        "image_url": url,
        "promt": promt
    }
]

POST /products/images
Запрос:
[
    {
        "id": id,
        "image": url,
        "promt": string
    },
    {
        "id": id,
        "image": url,
        "promt": string
    }
]

Ответ:
[
    {
        "id": id,
        "image": string,
        "image_url": url,
        "promt": string
    },
    {
        "id": id,
        "image": string,
        "image_url": url,
        "promt": string
    }
]

GET /search
Параметры:
 q
 limit

Запрос:
GET /search?q=...&limit=...

Ответ:
[
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": string,
        "image_url": url,
        "score": float
    },
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": string,
        "image_url": url,
        "score": float
    }

]

GET /search/text
Параметры:
 q
 limit

Запрос:
GET /search?q=...&limit=...

Ответ:
[
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": string,
        "image_url": url,
        "score": float
    },
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": string,
        "image_url": url,
        "score": float
    }

]


GET /search/hyb
Параметры:
 q
 limit

Запрос:
GET /search?q=...&limit=...

Ответ:
[
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": string,
        "image_url": url,
        "score": float
    },
    {
        "id": int,
        "name": string,
        "type": string,
        "description": string,
        "image": string,
        "image_url": url,
        "score": float
    }

]


POST /product/image/edit
Параметры:
 id
 text

Запрос /product/image/edit?id=...&text=...

GET /search/image
Параметры:
 q
 limit

Запрос /search/image?q=url&limit=...