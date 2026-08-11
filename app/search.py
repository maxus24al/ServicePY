from app.qdrant_cl import client
from app.config import COLLECTION
from app.t2v import embed_query


def search(query: str, limit: int = 5):
    vector = embed_query(query)

    result = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=limit,
    )

    return result.points