from typing import List

from pydantic import BaseModel
from typing_extensions import Generic, TypeVar


ListResultT = TypeVar('ListResultT', bound=BaseModel)


class ListResponse(BaseModel, Generic[ListResultT]):
    result: list[ListResultT]
    offset: int
    limit: int
    has_more: bool

    def __init__(
            self,
            *,
            result: list[ListResultT],
            offset: int,
            limit: int,
            **__pydantic_kwargs__
    ):
        super().__init__(
            result=result,
            offset=offset,
            limit=limit,
            has_more=len(result) == limit,
            **__pydantic_kwargs__
        )