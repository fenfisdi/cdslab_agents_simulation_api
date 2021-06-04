from fastapi import FastAPI

from src.config import fastApiConfig

app = FastAPI(**fastApiConfig)
