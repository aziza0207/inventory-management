from starlette import status

from .. import schemas, crud, models
from fastapi import APIRouter, Depends, HTTPException
from ..database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/establishments",
                   tags=["establishments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[schemas.Establishment])
async def get_establishments(
        skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    return db.query(models.Establishment).offset(skip).limit(limit).all()


@router.get("/{establishment_id}/", response_model=schemas.Establishment)
async def get_establishment(establishment_id: int, db: Session = Depends(get_db)):
    db_establishment = crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")
    return db_establishment


@router.post("/", response_model=schemas.EstablishmentBase, status_code=status.HTTP_201_CREATED)
async def create_establishment(
        establishment: schemas.EstablishmentBase, db: Session = Depends(get_db)
):
    return crud.create_establishment(db=db, establishment=establishment)


@router.patch("/{establishment_id}/", status_code=status.HTTP_200_OK)
async def update_establishment(
        establishment_id: int,
        establishment: schemas.EstablishmentBase,
        db: Session = Depends(get_db),
):
    db_establishment = crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found!")
    return crud.update_establishment(db, establishment_id, establishment)


@router.delete(
    "/{establishment_id}/", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_establishment(establishment_id: int, db: Session = Depends(get_db)):
    db_establishment = crud.get_establishment(db, establishment_id=establishment_id)
    if db_establishment is None:
        HTTPException(status_code=404, detail="Establishment not found")
    db.delete(db_establishment)
    db.commit()
