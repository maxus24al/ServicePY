POST /product
Запрос:
{
    "id": int,
    "name": string,
    "description": string,
    "image": url,
    "promt": string
}

Ответ:
{
    "id": int,
    "image": string
}

POST /products
Запрос:
[
    {
        "id": int,
        "name": string,
        "description": string,
        "image": url,
        "promt": string
    },
    {
        "id": int,
        "name": string,
        "description": string,
        "image": url,
        "promt": string
    }
]

Ответ:
[
    {
        "id": int,
        "image": string
    },
    {
        "id": int,
        "image": string
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
        "description": string,
        "image": string,
        "score": float
    },
    {
        "id": int,
        "name": string,
        "description": string,
        "image": string,
        "score": float
    }

]

GET /products
Ответ:
[
    {
        "id": int,
        "name": string,
        "description": string,
        "image": string,
        "score": float
    },
    {
        "id": int,
        "name": string,
        "description": string,
        "image": string,
        "score": float
    }

]