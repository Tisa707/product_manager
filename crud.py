from sqlalchemy.orm import Session
from product_manager import models, schemas

def create_product(db: Session, product: schemas.ProductCreate):
    existing = db.query(models.Product).filter(
        models.Product.name == product.name,
        models.Product.description == product.description
    ).first()
    if existing:
        return existing  # Skip creating, return existing one
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).order_by(models.Product.id).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()
