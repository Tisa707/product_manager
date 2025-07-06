from fastapi import FastAPI, Depends, UploadFile, File, HTTPException,status,Query, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import pandas as pd
import io

from . import models, schemas, crud
from .database import SessionLocal, engine




models.Base.metadata.create_all(bind=engine)

app = FastAPI()
#app.mount("/", StaticFiles(directory="product_manager/static", html=True), name="static")
app.mount("/ui", StaticFiles(directory="product_manager/static", html=True), name="static")

#https://literate-cod-wr5q977xjvx937j6-8000.app.github.dev/products/clear

#https://literate-cod-wr5q977xjvx937j6-8000.app.github.dev/ui/

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=list[schemas.Product])
def read_products(
    response: Response,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    total = db.query(models.Product).count()
    response.headers["X-Total-Count"] = str(total)

    offset = (page - 1) * page_size
    products = crud.get_products(db, skip=offset, limit=page_size)
    return products

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, updated_product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.name = updated_product.name
    db_product.description = updated_product.description
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted"}

@app.post("/uploadfile/", response_model=list[schemas.Product])
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))

    inserted_products = []
    for _, row in df.iterrows():
        product_data = schemas.ProductCreate(
            name=row["name"],
            description=row["description"]
        )
        db_product = crud.create_product(db=db, product=product_data)
        inserted_products.append(db_product)

    return inserted_products

# #@app.delete("/products/clear", status_code=status.HTTP_204_NO_CONTENT)
# @app.delete("/products/clear")
# def clear_products(db: Session = Depends(get_db)):
#     db.query(models.Product).delete()
#     db.commit()
#     return {"message": "All products cleared"}

@app.get("/products/clear")
def clear_products_get(db: Session = Depends(get_db)):
    db.query(models.Product).delete()
    db.commit()
    return {"message": "All products cleared (GET)"}



