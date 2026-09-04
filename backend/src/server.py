from fastapi import FastAPI

from presentation.api.errors import register_errors
from presentation.api.routers import portal_router, logs_router


class Server:
    def __init__(self, app: FastAPI):
        self.__register_middlewares(app)
        self.__register_errors(app)
        self.__register_routers(app)
        self.__app = app

    @staticmethod
    def __register_routers(app: FastAPI):
        app.include_router(portal_router)
        app.include_router(logs_router)

    @staticmethod
    def __register_middlewares(app: FastAPI):
        pass

    @staticmethod
    def __register_errors(app: FastAPI):
        register_errors(app)

    def get_app(self):
        return self.__app
