# app/main.py
from fastapi import FastAPI
import models
import database
import routes

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(routes.router)
