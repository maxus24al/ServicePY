from fastapi import FastAPI, HTTPException

from app.qdrant_cl import create_collection
from app.products import add_product_with_image, add_product_without_image, add_image, Product, ProductImage, ProductWithImage, get_products
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

    response = add_product_without_image(
        id=product.id,
        name=product.name,
        description=product.description,
    )

    return response;



@app.post("/product_w_image")
async def create_product(product: ProductWithImage):


    image_description = image_des(product.image, product.promt)

    response = add_product_with_image(
        id=product.id,
        name=product.name,
        description=product.description,
        image=image_description,
        promt=product.promt
    )

    return response;


@app.post("/product/image")
async def add_product_image(product: ProductImage):

    image_description = image_des(
        product.image,
        product.promt,
    )

    response = add_image(
        id=product.id,
        image=image_description,
        promt=product.promt,
    )

    return response


@app.post("/products")
def create_products(products: list[Product]):

    response = []

    for product in products:

        response.append(add_product_without_image(
            id=product.id, 
            name=product.name,
            description=product.description
        )
)
    return response

@app.post("/products_w_image")
def create_products(products: list[ProductWithImage]):

    response = []

    for product in products:

        image_description = image_des(product.image, product.promt)

        response.append(add_product_with_image(
            id=product.id, 
            name=product.name,
            description=product.description,
            image=image_description,
            promt=product.promt
        )
)
    return response

@app.post("/products/images")
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
                promt=product.promt,
            )
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