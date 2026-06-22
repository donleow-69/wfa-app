"""Shared rate-limiter instance — per-IP and per-user request throttling.

In-memory storage (slowapi default) is fine for a single Render instance. If
the app ever scales to multiple instances, switch to a shared Redis backend
via Limiter(storage_uri=...).
"""

from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address

from .auth import decode_token

limiter = Limiter(key_func=get_remote_address)


def user_or_ip_key(request) -> str:
    """Rate-limit key: signed-in user id if present, else client IP."""
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = decode_token(token)
            return f"user:{payload['sub']}"
        except (JWTError, KeyError):
            pass
    return f"ip:{get_remote_address(request)}"
