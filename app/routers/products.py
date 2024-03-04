from typing import Annotated
from starlette import status
from .. import crud, models, schemas
from fastapi import APIRouter, Depends, HTTPException
from ..database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/products",
                   tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[schemas.Product], status_code=status.HTTP_200_OK)
async def get_products(db: db_dependency, skip: int = 0, limit: int = 20):
    return db.query(models.Product).offset(skip).limit(limit).all()


@router.get("/{product_id}/", response_model=schemas.Product, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: db_dependency):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/", response_model=schemas.ProductBase, status_code=status.HTTP_201_CREATED)
async def create_product(product: schemas.ProductBase, db: db_dependency):
    return crud.create_product(db=db, product=product)


@router.patch("/{product_id}/", status_code=status.HTTP_200_OK)
async def update_product(db: db_dependency,
                         product_id: int, product: schemas.ProductBase
                         ):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found!")
    return crud.update_product(db=db, product_id=product_id, product=product)


@router.delete("/{product_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: db_dependency):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
