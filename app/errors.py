from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class APIError(Exception):
    def __init__(self, status_code, code, message, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}

    def to_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        )


class UnsupportedCurrencyError(APIError):
    def __init__(self, currency, supported):
        super().__init__(
            422,
            "unsupported_currency",
            f"Currency '{currency}' is not supported.",
            {"currency": currency, "supported_currencies": supported},
        )


class UnsupportedCorridorError(APIError):
    def __init__(self, corridor, supported):
        super().__init__(
            422,
            "unsupported_corridor",
            f"No exchange rate is configured for corridor '{corridor}'.",
            {"corridor": corridor, "supported_corridors": supported},
        )


class CollectionNotFoundError(APIError):
    def __init__(self, collection_id):
        super().__init__(
            404,
            "collection_not_found",
            f"No collection exists with id '{collection_id}'.",
            {"collection_id": collection_id},
        )


class QuoteNotFoundError(APIError):
    def __init__(self, quote_id):
        super().__init__(
            404,
            "quote_not_found",
            f"No quote exists with id '{quote_id}'.",
            {"quote_id": quote_id},
        )


class QuoteExpiredError(APIError):
    def __init__(self, quote_id, rate_expires_at):
        super().__init__(
            409,
            "quote_expired",
            "This quote has expired; request a fresh quote before executing.",
            {"quote_id": quote_id, "rate_expires_at": rate_expires_at},
        )


class CollectionNotCompletedError(APIError):
    def __init__(self, collection_id, current_status):
        message = (
            "The collection must be 'completed' before a conversion can be "
            f"executed (current status: '{current_status}')."
        )
        super().__init__(
            409,
            "collection_not_completed",
            message,
            {
                "collection_id": collection_id,
                "current_status": current_status,
                "required_status": "completed",
            },
        )


def api_error_handler(request, exc):
    return exc.to_response()


def validation_error_handler(request, exc):
    errors = []
    for err in exc.errors():
        parts = []
        for part in err.get("loc", []):
            if part != "body":
                parts.append(str(part))
        errors.append(
            {
                "field": ".".join(parts),
                "type": err.get("type"),
                "message": err.get("msg"),
            }
        )
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": "One or more request fields are invalid.",
            "details": {"errors": errors},
        },
    )


def unhandled_exception_handler(request, exc):
    """
    Catch anything unexpected so we never leak a stack trace.
    """
    return JSONResponse(
        status_code=500,
        content={
            "code": "internal_error",
            "message": "An unexpected error occurred.",
            "details": {},
        },
    )
