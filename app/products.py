from qdrant_client.models import PointStruct, PointVectors, SparseVector
from app.qdrant_cl import client, local_sparse_model
from fastembed import SparseTextEmbedding 
from app.config import COLLECTION
from app.t2v import embed_doc, lemmatize
from app.i2t import image_ind

from pydantic import BaseModel


class ProductImage(BaseModel):
    id: int
    image: str
    promt: str


class Product(BaseModel):
    id: int
    name: str
    type: str
    description: str
    image_t: str = ""
    image_ind: str = ""
    promt: str = ""





def add_product(
    id: int,
    type: str,
    name: str,
    description: str,
):
    
    full_text = f"{name} {type} {description}"
    raw_sparse = list(local_sparse_model.embed([full_text]))[0]
    
    sparse_vector = SparseVector(
        indices=raw_sparse.indices.tolist(),
        values=raw_sparse.values.tolist()
    )

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=id,
                vector={
                    
                    "name": embed_doc(name),
                    "type": embed_doc(type),
                    "description": embed_doc(description),
                    "text_sparse": sparse_vector
                },
                payload={
                    "name": name,
                    "type": type,
                    "type_keyword": type,
                    "description": description,
                },
            )
        ],
    )

    return {
        "id": id,
        "name": name,
        "type": type,
        "description": description,
    }

def add_product_w_image_t(
    id: int,
    name: str,
    type: type,
    description: str,
    image: str,
    image_url: str,
    promt: str,
):
    
    full_text = f"{name} {type} {description}"
    raw_sparse = list(local_sparse_model.embed([full_text]))[0]
    
    sparse_vector = SparseVector(
        indices=raw_sparse.indices.tolist(),
        values=raw_sparse.values.tolist()
    )

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=id,
                vector={
                    
                    "name": embed_doc(name),
                    "type": embed_doc(type),
                    "description": embed_doc(description),
                    "image": embed_doc(image),
                    "text_sparse": sparse_vector
                },
                payload={
                    "name": name,
                    "type": type,
                    "type_keyword": type,
                    "description": description,
                    "image": image,
                    "image_url": image_url,
                    "promt": promt,
                },
            )
        ],
    )

    return {
        "id": id,
        "name": name,
        "type": type,
        "description": description,
        "image": image,
        "promt": promt,
    }


def add_product_w_image_i(
    id: int,
    name: str,
    type: type,
    description: str,
    image_url: str,
):
    
    full_text = f"{name} {type} {description}"
    raw_sparse = list(local_sparse_model.embed([full_text]))[0]
    
    sparse_vector = SparseVector(
        indices=raw_sparse.indices.tolist(),
        values=raw_sparse.values.tolist()
    )

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=id,
                vector={
                    
                    "name": embed_doc(name),
                    "type": embed_doc(type),
                    "description": embed_doc(description),
                    "image_ind": image_ind(image_url),
                    "text_sparse": sparse_vector
                },
                payload={
                    "name": name,
                    "type": type,
                    "type_keyword": type,
                    "description": description,
                },
            )
        ],
    )

    return {
        "id": id,
        "name": name,
        "type": type,
        "description": description,
    }


def add_image(
    id: int,
    image: str,
    image_url: str,
    promt: str,
):
    points = client.retrieve(
        collection_name=COLLECTION,
        ids=[id],
        with_payload=False,
    )

    if not points:
        raise ValueError(f"Product with id={id} not found")

    client.update_vectors(
        collection_name=COLLECTION,
        points=[
            PointVectors(
                id=id,
                vector={
                    "image": embed_doc(image),
                    "image_ind": image_ind(image_url),
                },
            )
        ],
    )

    client.set_payload(
        collection_name=COLLECTION,
        payload={
            "image": image,
            "promt": promt,
        },
        points=[id],
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
            "type": point.payload.get("type"),
            "description": point.payload.get("description"),
            "image": point.payload.get("image"),
            "image_url": point.payload.get("image_url"),
            "lem_text": point.payload.get("lem_text"),
            "promt": point.payload.get("promt"),
        }
        for point in points
    ]

def edit_image(
    id: int,
    image: str,
):
    points = client.retrieve(
        collection_name=COLLECTION,
        ids=[id],
        with_payload=False,
    )

    if not points:
        raise ValueError(f"Product with id={id} not found")

    client.update_vectors(
        collection_name=COLLECTION,
        points=[
            PointVectors(
                id=id,
                vector={
                    "image": embed_doc(image),
                },
            )
        ],
    )

    client.set_payload(
        collection_name=COLLECTION,
        payload={
            "image": image,
        },
        points=[id],
    )

    return {
        "id": id,
        "image": image,
    }