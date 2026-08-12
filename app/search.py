from app.qdrant_cl import client
from app.config import COLLECTION
from app.t2v import embed_query
from qdrant_client import models


def search(q: str, limit: int = 5):
    vector = embed_query(q)

    result = client.query_points(
        collection_name=COLLECTION,
        prefetch=[
            models.Prefetch(
                query=vector,
                using="name",
                limit=50
            ),
            models.Prefetch(
                query=vector,
                using="description",
                limit=50
            ),
            models.Prefetch(
                query=vector,
                using="image",
                limit=50
            ),
                
        ],
        query=models.RrfQuery(
            rrf=models.Rrf(
                weights=[
                    0.45,
                    0.35,
                    0.2
                ]
            )
        ),
        limit=limit,
    )

    return result.points