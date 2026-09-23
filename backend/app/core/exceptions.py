from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, code: int = 1, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "请求失败"
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": detail, "data": None},
    )
