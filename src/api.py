from fastapi import FastAPI

from src.config import fastApiConfig
from src.routes import execution_routes

app = FastAPI(**fastApiConfig)

app.include_router(execution_routes)
