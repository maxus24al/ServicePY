from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from app.qdrant_cl import create_collection
from app.products import add_product, add_product_w_image, add_image, Product, ProductImage, get_products, edit_image
from app.search import search
from app.i2t import image_des

app = FastAPI()

API_TOKEN = os.environ["API_TOKEN"]

# @app.post("/image-description")
# async def image_description(file: UploadFile = File(...)):
#     path = f"/tmp/{file.filename}"

#     with open(path, "wb") as f:
#         f.write(await file.read())

#     return {"description": image_des(path)}


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