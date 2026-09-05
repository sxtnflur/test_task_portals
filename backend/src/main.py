import asyncio
from contextlib import asynccontextmanager

from db import engine
from fastapi import FastAPI
from infra.db import create_all_tables
from server import Server


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables(engine)
    yield


def create_app(*args, **kwargs):
    return Server(FastAPI(
        root_path='/api/v1',
        version='1.0.0',
        lifespan=lifespan
    )).get_app()

