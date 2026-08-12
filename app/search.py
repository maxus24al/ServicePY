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
                limit=15
            ),
            models.Prefetch(
                query=vector,
                using="description",
                limit=15
            ),
            models.Prefetch(
                query=vector,
                using="image",
                limit=15
            ),
                
        ],
        query=models.RrfQuery(
            rrf=models.Rrf(
                k=15,
                weights=[
                    0.15,
                    0.75,
                    0.1
                ]
            )
        ),
        limit=limit,
    )

    return result.points