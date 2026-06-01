from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .errors import (
    APIError,
    api_error_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from .routers import collections, conversions

app = FastAPI(
    title="Transika Payment Collections & Conversion API",
    version="1.0.0",
)

app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(collections.router)
app.include_router(conversions.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
