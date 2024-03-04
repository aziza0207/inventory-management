import pytest
from starlette import status
from fastapi.testclient import TestClient
from ..models import Establishment
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from ..main import app
from ..routers.establishments import get_db

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


app.dependency_overrides[get_db] = override_get_db
db = override_get_db()

client = TestClient(app)


@pytest.fixture()
def test_establishment():
    establishments = Establishment(name=f"Test Establishment",
                                   description="Description of Test Product",
                                   location="Address of Establishment"
                                   )

    db = TestingSessionLocal()
    db.add(establishments)
    db.commit()
    yield establishments
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM establishment;"))
        connection.commit()


def test_get_all_establishments(test_establishment):
    response = client.get("/api/establishments/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["name"] == test_establishment.name
    assert response.json()[0]["id"] == test_establishment.id
    assert response.json()[0]["name"] == test_establishment.name


def test_get_establishment(test_establishment):
    response = client.get("/api/establishments/" + f"{test_establishment.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_establishment.id
    assert response.json()["name"] == test_establishment.name
    assert response.json()["description"] == test_establishment.description


def test_create_establishment(test_establishment):
    payload = {"name": "New Establishment",
               "description": "Test Product",
               "location": "New location"}

    response = client.post("/api/establishments/", json=payload)
    assert response.status_code == 201
    db = TestingSessionLocal()
    model = db.query(Establishment).filter(Establishment.name == payload["name"]).first()
    assert model.name == payload["name"]
    assert model.description == payload["description"]
    assert model.location == payload["location"]


@pytest.mark.skip
def test_update_establishment(test_establishment):
    payload = {"name": "Update Establishment Name",
               "description": "Update Establishment Description",
               "location": "Update location",
               "opening_hours": None}
    response = client.patch("/api/establishments/" + f"{test_establishment.id}", json=payload)
    assert response.status_code == 200
    db = TestingSessionLocal()
    model = db.query(Establishment).filter(Establishment.id == test_establishment.id).first()
    assert model.name == payload["name"]
    assert model.description == payload["description"]
    assert model.location == payload["location"]


def test_delete_establishment(test_establishment):
    response = client.delete("/api/establishments/" + f"{test_establishment.id}")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Establishment).filter(Establishment.id == test_establishment.id).first()
    assert model is None
