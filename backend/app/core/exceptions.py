"""
Custom exceptions and FastAPI exception handlers.

All API error responses follow the shape:
    {"error": "ERROR_CODE", "message": "Human-readable message", "details": [...optional...]}

Stack traces and credentials are never exposed in responses.
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("neerniti")


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, resource_id: object) -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} '{resource_id}' not found")


class BusinessError(Exception):
    """Raised for application-level rule violations that should be surfaced to the caller."""

    def __init__(self, message: str, code: str = "BUSINESS_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class UnauthorizedError(Exception):
    """Raised when an operation requires an authorization credential that is missing or invalid."""

    def __init__(self, message: str = "Unauthorized") -> None:
        self.message = message
        super().__init__(message)


class ExternalServiceError(Exception):
    """Raised when a call to an external service (e.g. weather API) fails."""

    def __init__(self, service: str, message: str) -> None:
        self.service = service
        self.message = message
        super().__init__(f"{service}: {message}")


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------

async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": "NOT_FOUND",
            "message": str(exc),
            "resource": exc.resource,
        },
    )


async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": exc.code, "message": exc.message},
    )


async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"error": "UNAUTHORIZED", "message": exc.message},
    )


async def external_service_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": "EXTERNAL_SERVICE_ERROR",
            "message": f"External service '{exc.service}' is unavailable: {exc.message}",
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Pydantic v2 error dicts may contain Exception objects in 'ctx' — serialise them to strings
    def _safe_errors(errors: list) -> list:
        safe = []
        for err in errors:
            safe_err = {}
            for k, v in err.items():
                if k == "ctx" and isinstance(v, dict):
                    safe_err[k] = {ck: str(cv) for ck, cv in v.items()}
                else:
                    safe_err[k] = v
            safe.append(safe_err)
        return safe

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": _safe_errors(exc.errors()),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP_ERROR", "message": exc.detail},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An internal server error occurred. Please try again later.",
        },
    )
