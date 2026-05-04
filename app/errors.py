from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_response(code: int, message: str,path: str) -> JSONResponse:
    return JSONResponse(
        status_code = code,
        content = {
            "error": True,
            "code": code,
            "message": message,
            "path": path
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(
        code=exc.status_code,
        message = exc.detail,
        path=str(request.url.path),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    
    return JSONResponse(
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
        content = {
            "error" : True,
            "code" : 422,
            "message" : "Validation failed",
            "details" : errors,
            "path" : str(request.url.path),
        }
    )


async def unhandled_exception_handler(request: Request, exc : Exception):
    return error_response(
        code=500,
        message = "An unexpected error occured. Please try again later.",
        path = str(request.url.path),

    )