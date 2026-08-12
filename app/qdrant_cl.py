from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION,
    VECTOR_SIZE,
)

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
)


def create_collection():
    if client.collection_exists(COLLECTION):
        return

    client.delete_collection(COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            "name": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "type": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "description": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "image": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        },
    )