from fastapi import FastAPI
from server import Server


def create_app(*args, **kwargs):
    return Server(FastAPI(
        root_path='/api/v1',
        version='1.0.0'
    )).get_app()

