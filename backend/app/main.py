import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings

logger = logging.getLogger("tio")

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Investigation-based UPSC learning platform backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error(status_code: int, message: str, data=None, headers=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "data": data, "message": message},
        headers=headers,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return _error(exc.status_code, str(exc.detail), headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return _error(422, "Validation failed", data={"errors": errors})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log details server-side; never leak internals to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _error(500, "Internal server error")


@app.get("/health", tags=["Health"])
def health():
    return {"success": True, "data": {"status": "ok"}, "message": ""}


app.include_router(api_router, prefix="/api/v1")
