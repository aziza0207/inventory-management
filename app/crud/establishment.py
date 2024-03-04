from sqlalchemy.orm import Session

from app import models, schemas


def get_establishment(db: Session, establishment_id: int):
    return (
        db.query(models.Establishment)
        .filter(models.Establishment.id == establishment_id)
        .first()
    )


def create_establishment(db: Session, establishment: schemas.EstablishmentBase):
    db_establishment = models.Establishment(
        name=establishment.name,
        description=establishment.description,
        location=establishment.location,
        opening_hours=establishment.opening_hours,
    )
    db.add(db_establishment)
    db.commit()
    db.refresh(db_establishment)
    return db_establishment


def update_establishment(db: Session, establishment_id: int, establishment):
    db_establishment = (
        db.query(models.Product).filter(models.Product.id == establishment_id).first()
    )
    db_establishment.name = establishment.name
    db_establishment.description = establishment.description
    db.add(db_establishment)
    db.commit()
    return db_establishment
