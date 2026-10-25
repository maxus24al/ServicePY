from app.qdrant_cl import client, local_sparse_model
from fastembed import SparseTextEmbedding 
from app.config import COLLECTION
from app.t2v import embed_query, lemmatize
from qdrant_client import models



def search(q: str, limit: int = 5):
    vector = embed(q)

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
                using="type",
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
            models.Prefetch(query=query_dense_vector, using="name", limit=50, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="type", limit=50, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="description", limit=50, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="image", limit=50, filter=exclude_filter),
            models.Prefetch(query=query_sparse_vector, using="text_sparse", limit=50, filter=exclude_filter)
        ],
        query=models.FusionQuery(
            fusion=models.Fusion.DBSF
        ),
        limit=remaining_limit,
        with_payload=True
    )
    
    return final_results + search_result.points

from collections import defaultdict


def hybrid_search_debug(q: str, limit: int = 10):
    """
    Возвращает словарь:
      - final: результаты после DBSF (как в обычном hybrid_search)
      - raw: {using: [(id, score), ...]} — сырые скоры по каждому вектору
      - overlap: какие id попали в топ каждого retriever'а
    """
    final_results = []
    all_found_ids = set()

    # --- 1. Точное совпадение по type_keyword ---
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
        return {"final": final_results[:limit], "raw": {}, "overlap": {}}

    remaining_limit = limit - len(final_results)

    # --- 2. Текстовый фильтр по type ---
    text_filter_must = [
        models.FieldCondition(key="type", match=models.MatchText(text=q))
    ]
    text_filter_must_not = (
        [models.HasIdCondition(has_id=list(all_found_ids))]
        if all_found_ids else []
    )

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
        return {"final": final_results[:limit], "raw": {}, "overlap": {}}

    remaining_limit = limit - len(final_results)

    # --- 3. Подготовка векторов ---
    raw_query_sparse = list(local_sparse_model.embed([q]))[0]
    query_sparse_vector = models.SparseVector(
        indices=raw_query_sparse.indices.tolist(),
        values=raw_query_sparse.values.tolist()
    )
    query_dense_vector = embed_query(q)

    exclude_filter = None
    if all_found_ids:
        exclude_filter = models.Filter(
            must_not=[models.HasIdCondition(has_id=list(all_found_ids))]
        )

    # --- 4. СЫРЫЕ скоры по каждому retriever'у отдельно ---
    # Делаем отдельные query_points БЕЗ prefetch/fusion — это и есть нативные скоры.
    retrievers = {
        "name":        (query_dense_vector, "name"),
        "type":        (query_dense_vector, "type"),
        "description": (query_dense_vector, "description"),
        "image":       (query_dense_vector, "image"),
        "text_sparse": (query_sparse_vector, "text_sparse"),
    }

    raw = {}
    for name, (vec, using) in retrievers.items():
        res = client.query_points(
            collection_name=COLLECTION,
            query=vec,
            using=using,
            limit=50,
            query_filter=exclude_filter,
            with_payload=False,
        )
        raw[name] = [(p.id, p.score) for p in res.points]

    # --- 5. Итоговый DBSF (как в боевом hybrid_search) ---
    search_result = client.query_points(
        collection_name=COLLECTION,
        prefetch=[
            models.Prefetch(query=query_dense_vector, using="name",        limit=50, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="type",        limit=50, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="description", limit=50, filter=exclude_filter),
            models.Prefetch(query=query_dense_vector, using="image",       limit=50, filter=exclude_filter),
            models.Prefetch(query=query_sparse_vector, using="text_sparse", limit=50, filter=exclude_filter),
        ],
        query=models.FusionQuery(fusion=models.Fusion.DBSF),
        limit=remaining_limit,
        with_payload=True,
    )

    # --- 6. Overlap: какие id в топ-10 каждого retriever'а ---
    overlap = {name: {pid for pid, _ in pairs[:10]} for name, pairs in raw.items()}

    return {
        "final": final_results + search_result.points,
        "raw": raw,
        "overlap": overlap,
    }


def print_dbsf_diagnostics(q: str, limit: int = 10):
    """
    Печатает таблицу: для каждого retriever'а — разброс скоров и позицию правильных id.
    Плюс проверяет, не «съедает» ли DBSF остальных.
    """
    data = hybrid_search_debug(q, limit)
    raw = data["raw"]

    if not raw:
        print("Сработали точные фильтры (type_keyword / type), DBSF не вызывался.")
        return

    print(f"\n=== Запрос: {q!r} ===")
    print(f"{'retriever':<14} {'min':>7} {'max':>7} {'range':>8} {'mean':>7} {'std':>7}")
    for name, pairs in raw.items():
        if not pairs:
            continue
        scores = [s for _, s in pairs]
        import statistics
        mn, mx = min(scores), max(scores)
        mean = statistics.mean(scores)
        std = statistics.pstdev(scores) if len(scores) > 1 else 0.0
        print(f"{name:<14} {mn:7.4f} {mx:7.4f} {mx - mn:8.4f} {mean:7.4f} {std:7.4f}")

    # Пересечения топ-10
    names = list(raw.keys())
    print("\nПересечение топ-10 между retriever'ами:")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            inter = data["overlap"][a] & data["overlap"][b]
            print(f"  {a:<12} ∩ {b:<12}: {len(inter)} общих id")

    # Позиции финальных id в каждом retriever'е
    print("\nГде в каждом retriever'е находятся id из финального топ-N:")
    for point in data["final"]:
        pid = point.id
        positions = []
        for name, pairs in raw.items():
            pos = next((idx for idx, (i, _) in enumerate(pairs) if i == pid), None)
            positions.append(f"{name}={pos if pos is not None else '—'}")
        print(f"  id={pid}: " + ", ".join(positions))