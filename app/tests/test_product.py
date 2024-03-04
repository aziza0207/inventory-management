import pytest
from starlette import status
from fastapi.testclient import TestClient
from ..models import Product
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from ..main import app
from ..routers.products import get_db as product_db

SQLALCHEMY_DATABASE_URL = "postgresql://fastapi:fastapi@test-db/test"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       poolclass=StaticPool, )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()


app.dependency_overrides[product_db] = override_get_db
db = override_get_db()

client = TestClient(app)


@pytest.fixture()
def test_product():
    products = Product(name="Test Product",
                       description="Test Product",
                       price=100,
                       quantity=100)
    db = TestingSessionLocal()
    db.add(products)
    db.commit()
    yield products
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM product;"))
        connection.commit()


def test_get_all_products(test_product):
    response = client.get("/api/products/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == test_product.id
    assert response.json()[0]["name"] == test_product.name
    assert response.json()[0]["description"] == test_product.description
    assert response.json()[0]["price"] == test_product.price
    assert response.json()[0]["quantity"] == test_product.quantity


def test_get_product(test_product):
    response = client.get("/api/products/" + f"{test_product.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_product.id
    assert response.json()["name"] == test_product.name
    assert response.json()["description"] == test_product.description
    assert response.json()["price"] == test_product.price
    assert response.json()["quantity"] == test_product.quantity


def test_create_product(test_product):
    payload = {"name": "New Product",
               "description": "Test Product",
               "price": 150,
               "quantity": 200}
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 201
    db = TestingSessionLocal()
    model = db.query(Product).filter(Product.name == payload["name"]).first()
    assert model.name == payload["name"]
    assert model.description == payload["description"]
    assert model.price == payload["price"]
    assert model.quantity == payload["quantity"]


def test_update_product(test_product):
    payload = {"name": "Update Product Name",
               "description": "Update Product Description",
               "price": 250,
               "quantity": 100}
    response = client.patch("/api/products/" + f"{test_product.id}", json=payload)
    assert response.status_code == 200
    db = TestingSessionLocal()
    model = db.query(Product).filter(Product.id == test_product.id).first()
    assert model.name == payload["name"]
    assert model.description == payload["description"]
    assert model.price == payload["price"]
    assert model.quantity == payload["quantity"]


def test_delete_product(test_product):
    response = client.delete("/api/products/" + f"{test_product.id}")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Product).filter(Product.id == test_product.id).first()
    assert model is None
