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
    "id": id,
    "name": name,
    "description": description,
    "image": image,
    "promt": promt
}

POST /product/image
Запрос:
{
    "id": id,
    "image": string,
    "promt": string
}

Ответ:
{
    "id": id,
    "image": url,
    "promt": string
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
        "id": id,
        "name": name,
        "description": description,
        "image": image,
        "promt": promt
    },
    {
        "id": id,
        "name": name,
        "description": description,
        "image": image,
        "promt": promt
    }
]

POST /products/image
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
        "promt": string
    },
    {
        "id": id,
        "image": string,
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

POST /product/image/edit
Параметры:
 id
 text

Запрос /product/image/edit?id=...&text=...