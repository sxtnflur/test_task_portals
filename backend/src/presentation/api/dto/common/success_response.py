from presentation.api.dto.common.base_response import BaseResponse
from pydantic import BaseModel
from typing_extensions import TypeVar, Generic
from typing_inspection.typing_objects import NoneType

PayloadT = TypeVar('PayloadT', bound=BaseModel | NoneType)


class SuccessResponse(BaseResponse, Generic[PayloadT]):
    ok: bool = True
    payload: PayloadT | None = None

    def __init__(
        self,
        payload: PayloadT = None,
        **__pydantic_kwargs__
    ):
        __pydantic_kwargs__.setdefault('ok', True)
        super().__init__(payload=payload, **__pydantic_kwargs__)

    @classmethod
    def create(cls, payload: PayloadT) -> 'SuccessResponse':
        return cls(
            ok=True, payload=payload
        )


EmptySuccessResponse = SuccessResponse[None]
