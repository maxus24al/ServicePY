from qdrant_client.models import PointStruct

from app.qdrant_cl import client
from app.config import COLLECTION
from app.t2v import embed_doc

from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    description: str


class ProductImage(BaseModel):
    id: int
    image: str
    promt: str


class ProductWithImage(BaseModel):
    id: int
    name: str
    description: str
    image: str
    promt: str


def add_product_without_image(
    id: int,
    name: str,
    description: str,
):
    text = f"""
name: {name}
description: {description}
"""

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=id,
                vector=embed_doc(text),
                payload={
                    "name": name,
                    "description": description,
                },
            )
        ],
    )

    return {
        "id": id,
        "name": name,
        "description": description,
    }


def add_product_with_image(
    id: int,
    name: str,
    description: str,
    image: str,
    promt: str,
):
    text = f"""
name: {name}
description: {description}
image: {image}
"""

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=id,
                vector=embed_doc(text),
                payload={
                    "name": name,
                    "description": description,
                    "image": image,
                    "promt": promt,
                },
            )
        ],
    )

    return {
        "id": id,
        "name": name,
        "description": description,
        "image": image,
        "promt": promt,
    }


def add_image(
    id: int,
    image: str,
    promt: str,
):
    points = client.retrieve(
        collection_name=COLLECTION,
        ids=[id],
        with_payload=True,
    )

    if not points:
        raise ValueError(f"Product with id={id} not found")

    product = points[0]

    name = product.payload["name"]
    description = product.payload["description"]

    text = f"""
name: {name}
description: {description}
image: {image}
"""

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=id,
                vector=embed_doc(text),
                payload={
                    **product.payload,
                    "image": image,
                    "promt": promt,
                },
            )
        ],
    )

    return {
        "id": id,
        "image": image,
        "promt": promt,
    }


def get_products():
    points, _ = client.scroll(
        collection_name=COLLECTION,
        with_payload=True,
    )

    return [
        {
            "id": point.id,
            "name": point.payload.get("name"),
            "description": point.payload.get("description"),
            "image": point.payload.get("image"),
            "promt": point.payload.get("promt"),
        }
        for point in points
    ]