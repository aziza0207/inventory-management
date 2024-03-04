from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: int
    quantity: int


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True


class EstablishmentBase(BaseModel):
    name: str
    description: str | None = None
    location: str
    opening_hours: str | None = None


class Establishment(EstablishmentBase):
    id: int

    class Config:
        orm_mode = True
