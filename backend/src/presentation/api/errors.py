from application.errors import NotFoundError
from domain.common.errors import DomainError
from fastapi import FastAPI, Request, status
from presentation.api.dto.common import ErrorResponse
from starlette.responses import JSONResponse


def register_errors(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def portal_not_found_handler(
            request: Request, exception: NotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(type(exception), exception.message).model_dump(),
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exception: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(type(exception), exception.message).model_dump(),
        )
    return app
