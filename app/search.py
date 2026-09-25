from app.qdrant_cl import client
from fastembed import SparseTextEmbedding 
from app.config import COLLECTION
from app.t2v import embed_query
from qdrant_client import models


local_sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")

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
                using="type",
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
                    0.1,
                    0.4,
                    0.4,
                    0.1
                ]
            )
        ),
        limit=limit,
    )

    return result.points

def t_search(q: str, limit: int = 10):
    
    raw_query_sparse = list(local_sparse_model.embed([q]))[0]
    
    query_sparse_vector = models.SparseVector(
        indices=raw_query_sparse.indices.tolist(),
        values=raw_query_sparse.values.tolist()
    )

    search_result = client.query_points(
        collection_name=COLLECTION,
        query=query_sparse_vector,
        using="text_sparse", 
        limit=limit,
        with_payload=True
    )
    return search_result


def hybrid_search(q: str, limit: int = 10):
    q_filter, _ = client.scroll(
        collection_name=COLLECTION,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="type",
                    match=models.MatchText(text=q)
                )
            ]
        ),
        limit=limit,
        with_payload=True
    )

    if q_filter:
        return q_filter

    raw_query_sparse = list(local_sparse_model.embed([q]))[0]
    query_sparse_vector = models.SparseVector(
        indices=raw_query_sparse.indices.tolist(),
        values=raw_query_sparse.values.tolist()
    )

    query_dense_vector = embed_query(q) 
    
    search_result = client.query_points(
        collection_name=COLLECTION,
        
        prefetch=[
            models.Prefetch(
                query=query_dense_vector,
                using="name",
                limit=15
            ),
            models.Prefetch(
                query=query_dense_vector,
                using="type",
                limit=15
            ),
            models.Prefetch(
                query=query_dense_vector,
                using="description",
                limit=15
            ),
            models.Prefetch(
                query=query_dense_vector,
                using="image",
                limit=15
            ),
            models.Prefetch(
                query=query_sparse_vector,
                using="text_sparse",
                limit=15
            )
        ],
        
        query=models.RrfQuery(
            rrf=models.Rrf(
                k=15,
                weights=[
                    0.5,
                    0.2,
                    0.1,
                    0.1,
                    1
                ]
            )
        ),
        limit=limit,
        with_payload=True
    )
    
    return search_result.points