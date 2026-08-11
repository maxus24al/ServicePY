from qdrant_client.models import PointStruct

from app.qdrant_cl import client
from app.config import COLLECTION
from app.t2v import embed_doc
from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    description: str
    image: str
    promt: str


def add_product(id: int, name: str, description: str, image: str, promt: str):
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
                    "promt": promt
                },
            )
        ],
    )

    return {"id": id, "image": image, "promt": promt};

def get_products():
    points, _ = client.scroll(
        collection_name=COLLECTION,
        with_payload=True,
    )

    return [
        {
            "id": point.id,
            "name": point.payload["name"],
            "description": point.payload["description"],
            "image": point.payload["image"],
            "promt": point.payload["promt"]
        }
        for point in points
    ]
    