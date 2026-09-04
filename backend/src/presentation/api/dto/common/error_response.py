from presentation.api.dto.common.base_response import BaseResponse, ErrorData
from typing_extensions import Type


class ErrorResponse(BaseResponse):
    ok: bool = False

    def __init__(
            self,
            exception: Type[Exception],
            detail: str,
            **__pydantinc_kwargs__
    ):
        super().__init__(
            ok=False,
            error=ErrorData(type=exception.__name__, detail=detail),
            **__pydantinc_kwargs__
        )
