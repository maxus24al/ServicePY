from fastapi import FastAPI, UploadFile, File, Form

from app.qdrant_cl import create_collection
from app.products import add_product, Product, get_products
from app.search import search
from app.i2t import image_des

app = FastAPI()



# @app.post("/image-description")
# async def image_description(file: UploadFile = File(...)):
#     path = f"/tmp/{file.filename}"

#     with open(path, "wb") as f:
#         f.write(await file.read())

#     return {"description": image_des(path)}

@app.on_event("startup")
def startup():
    create_collection()


@app.post("/product")
async def create_product(product: Product):


    image_description = image_des(product.image)

    response = add_product(
        id=product.id,
        name=product.name,
        description=product.description,
        image=image_description
    )

    return response;


@app.post("/products")
def create_products(products: list[Product]):

    response = []

    for product in products:

        image_description = image_des(product.image)

        response.append(add_product(
            id=product.id, 
            name=product.name,
            description=product.description,
            image=image_description)
)
    return response


@app.get("/search")
def search_products(q: str, limit: int = 5):
    points = search(q, limit)

    return [
        {
            "id": point.id,
            "name": point.payload["name"],
            "description": point.payload["description"],
            "image": point.payload["image"],
            "score": point.score,
        }
        for point in points
    ]

@app.get("/products")
def get_all_products():
    return get_products()