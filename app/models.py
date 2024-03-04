from sqlalchemy import Column, Integer, String, Time
from .database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)


class Establishment(Base):
    __tablename__ = "establishment"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    location = Column(String)
    opening_hours = Column(Time, nullable=True)
