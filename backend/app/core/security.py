"""
Simple API-key authentication for administrative endpoints.

The key is read from the X-API-Key request header and compared to the
ADMIN_API_KEY environment variable.  This is suitable for internal / local
use.  For a public-facing deployment, replace with a proper OAuth2 / JWT
implementation.
"""
from fastapi import Header
from app.core.config import settings
from app.core.exceptions import UnauthorizedError


async def require_admin_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    """
    FastAPI dependency that validates the X-API-Key header.

    Raises UnauthorizedError (→ HTTP 401) if the key is missing or wrong.
    """
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise UnauthorizedError("Invalid or missing admin API key.")
