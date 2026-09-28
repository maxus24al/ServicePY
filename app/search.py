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

from qdrant_client import models

def hybrid_search(q: str, limit: int = 10):
    final_results = []
    all_found_ids = set()

    scroll_records_f, _ = client.scroll(
        collection_name=COLLECTION,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="type_keyword",
                    match=models.MatchValue(value=q)
                )
            ]
        ),
        limit=limit,
        with_payload=True
    )
    
    for point in scroll_records_f:
        final_results.append(point)
        all_found_ids.add(point.id)
    
    if len(final_results) >= limit:
        return final_results[:limit]
        
    remaining_limit = limit - len(final_results)

    text_filter_must = [
        models.FieldCondition(
            key="type",
            match=models.MatchText(text=q)
        )
    ]
    
    if all_found_ids:
        text_filter_must_not = [models.HasIdCondition(has_id=list(all_found_ids))]
    else:
        text_filter_must_not = []

    scroll_records_s, _ = client.scroll(
        collection_name=COLLECTION,
        scroll_filter=models.Filter(
            must=text_filter_must,
            must_not=text_filter_must_not
        ),
        limit=remaining_limit,
        with_payload=True
    )

    for point in scroll_records_s:
        final_results.append(point)
        all_found_ids.add(point.id)

    if len(final_results) >= limit:
        return final_results[:limit]
        
    remaining_limit = limit - len(final_results)

    raw_query_sparse = list(local_sparse_model.embed([q]))[0]
    query_sparse_vector = models.SparseVector(
        indices=raw_query_sparse.indices.tolist(),
        values=raw_query_sparse.values.tolist()
    )

    query_dense_vector = embed_query(q) 
    
    exclude_filter = None
    if all_found_ids:
        exclude_filter = models.Filter(
            must_not=[
                models.HasIdCondition(has_id=list(all_found_ids))
            ]
        )
    
    search_result = client.query_points(
        collection_name=COLLECTION,
        prefetch=[
            models.Prefetch(query=query_dense_vector, using="name", limit=15, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="type", limit=15, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="description", limit=15, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="image", limit=15, filter=exclude_filter),
            models.Prefetch(query=query_sparse_vector, using="text_sparse", limit=15, filter=exclude_filter)
        ],
        query=models.RrfQuery(
            rrf=models.Rrf(
                k=15,
                weights=[0.5, 0.2, 0.1, 0.1, 1]
            )
        ),
        limit=remaining_limit,
        with_payload=True
    )
    
    return final_results + search_result.points
