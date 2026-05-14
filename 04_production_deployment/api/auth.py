"""
API key authentication.

The API expects a header `X-API-Key` on protected routes. The key is
compared against the value configured in settings.api_key. In production,
override the default via environment variable.

For a real production service, use rotated keys with hashing — this
implementation is simple by design (portfolio service).
"""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

from .config import settings


api_key_header = APIKeyHeader(name=settings.api_key_header_name, auto_error=False)


async def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Reject requests without a valid API key.

    Health and metrics endpoints skip this dependency. All prediction
    endpoints require it.
    """
    if api_key is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Missing {settings.api_key_header_name} header",
        )
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key
