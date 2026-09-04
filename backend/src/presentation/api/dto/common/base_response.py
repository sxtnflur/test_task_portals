from pydantic import BaseModel


class ErrorData(BaseModel):
    type: str
    detail: str


class BaseResponse(BaseModel):
    ok: bool = True
    payload: BaseModel | None = None
    error: ErrorData | None = None



