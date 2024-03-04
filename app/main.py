from fastapi import FastAPI
from . import models
from app.database import engine
from app.routers import product_router, establishment_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(product_router)
app.include_router(establishment_router)
