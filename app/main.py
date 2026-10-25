from fastapi import FastAPI, HTTPException, status, Header, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from app.qdrant_cl import create_collection, local_sparse_model
from app.products import add_product, add_product_w_image, add_image, Product, ProductImage, get_products, edit_image
from app.search import search, t_search, hybrid_search, hybrid_search_debug
from app.i2t import image_des

app = FastAPI()

API_TOKEN = os.environ["API_TOKEN"]

security_scheme = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

@app.on_event("startup")
def startup():
    create_collection()


@app.post("/product", dependencies=[Depends(verify_token)])
async def create_product(product: Product):

    if(product.image != ''):
        image_description = image_des(product.image, product.promt)

        response = add_product_w_image(
            id=product.id,
            name=product.name,
            type=product.type,
            description=product.description,
            image=image_description,
            image_url=product.image,
            promt=product.promt
        )

    else:
        response = add_product(
            id=product.id,
            name=product.name,
            type=product.type,
            description=product.description,
        )

    return response;


@app.post("/product/image", dependencies=[Depends(verify_token)])
async def add_product_image(product: ProductImage):

    image_description = image_des(
        product.image,
        product.promt,
    )

    response = add_image(
        id=product.id,
        image=image_description,
        image_url=product.image,
        promt=product.promt,
    )

    return response


@app.post("/products", dependencies=[Depends(verify_token)])
def create_products(products: list[Product]):

    response = []

    for product in products:

        if(product.image != ''):
            image_description = image_des(product.image, product.promt)
    
            response.append(add_product_w_image(
                id=product.id,
                name=product.name,
                type=product.type,
                description=product.description,
                image=image_description,
                image_url=product.image,
                promt=product.promt
            ))
    
        else:
            response.append(add_product(
                id=product.id,
                name=product.name,
                type=product.type,
                description=product.description,
            ))

    return response

@app.post("/products/images", dependencies=[Depends(verify_token)])
async def add_products_images(products: list[ProductImage]):

    response = []

    for product in products:
        image_description = image_des(
            product.image,
            product.promt,
        )

        response.append(
            add_image(
                id=product.id,
                image=image_description,
                image_url=image,
                promt=product.promt,
            )
        )

    return response

@app.get("/search", dependencies=[Depends(verify_token)])
def search_products(q: str, limit: int = 5):
    points = search(q, limit)

    return [
        {
            "id": point.id,
            "name": point.payload.get("name"),
            "type": point.payload.get("type"),
            "description": point.payload.get("description"),
            "lem_text": point.payload.get("lem_text"),
            "image": point.payload.get("image"),
            "promt": point.payload.get("promt"),
            "score": point.score,
        }
        for point in points
    ]

@app.get("/products", dependencies=[Depends(verify_token)])
def get_all_products():
    return get_products()

@app.post("/product/image/edit", dependencies=[Depends(verify_token)])
def edit_product_image(id: int, text: str):
    edit_image(id, text)


@app.get("/search/text", dependencies=[Depends(verify_token)])
def text_search(q: str = Query(..., min_length=2), limit: int = 10):
    search_result = t_search(q, limit)
    return [
        {
            "id": hit.id, 
            "score": hit.score, 
            "payload": hit.payload
        } 
        for hit in search_result.points
    ]

@app.get("/search/hyb", dependencies=[Depends(verify_token)])
def hyb_search(q: str = Query(..., min_length=2), limit: int = 10):
    search_result = hybrid_search(q=q, limit=limit)
    
    formatted_results = []
    for hit in search_result:
        formatted_results.append({
            "id": hit.id,
            "score": getattr(hit, "score", None), 
            "payload": hit.payload
        })
        
    return formatted_results


import statistics
from fastapi import Query, Depends


@app.get("/search/hyb/debug", dependencies=[Depends(verify_token)])
def hyb_search_debug_endpoint(q: str = Query(..., min_length=2), limit: int = 10):
    """
    Диагностика DBSF: возвращает финальный результат + сырые скоры по каждому retriever'у,
    статистику распределения и пересечения топ-10.
    """
    data = hybrid_search_debug(q=q, limit=limit)

    # --- финальный результат ---
    final_out = [
        {
            "id": p.id,
            "score": getattr(p, "score", None),
            "payload": p.payload,
        }
        for p in data["final"]
    ]

    # --- сырые скоры + статистика по каждому retriever'у ---
    raw_out = {}
    stats_out = {}
    for name, pairs in data["raw"].items():
        raw_out[name] = [{"id": pid, "score": score} for pid, score in pairs]

        if not pairs:
            stats_out[name] = None
            continue

        scores = [s for _, s in pairs]
        mn, mx = min(scores), max(scores)
        stats_out[name] = {
            "count": len(scores),
            "min": mn,
            "max": mx,
            "range": mx - mn,
            "mean": statistics.mean(scores),
            "std": statistics.pstdev(scores) if len(scores) > 1 else 0.0,
        }

    # --- позиции финальных id в каждом retriever'е ---
    positions_out = []
    for p in data["final"]:
        positions = {}
        for name, pairs in data["raw"].items():
            pos = next((idx for idx, (pid, _) in enumerate(pairs) if pid == p.id), None)
            positions[name] = pos  # None = не найден в топ-50 этого retriever'а
        positions_out.append({"id": p.id, "positions": positions})

    # --- overlap топ-10 между retriever'ами ---
    names = list(data["overlap"].keys())
    overlap_out = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            inter = data["overlap"][a] & data["overlap"][b]
            overlap_out[f"{a} ∩ {b}"] = sorted(inter)

    return {
        "query": q,
        "limit": limit,
        "final": final_out,
        "raw": raw_out,
        "stats": stats_out,
        "positions": positions_out,
        "overlap_top10": overlap_out,
    }