from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse

import cache
from db import get_session_factory
from models import User

API_KEY_HEADER = "API_KEY"
API_PREFIX = "/api/v1/"

# Paths that need no API key (Swagger UI and the hello-world route).
PUBLIC_PATHS = frozenset({"/", "/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"})


def _load_user_from_db(api_key: str) -> dict | None:
    with get_session_factory()() as session:
        user = session.query(User).filter(User.api_key == api_key).one_or_none()
        if user is None:
            return None
        return {"app": user.app, "endpoint_access": user.endpoint_access}


def find_user(api_key: str) -> dict | None:
    """Redis first, then PostgreSQL (the source of truth). Fill the cache on a miss."""
    user = cache.get_cached_user(api_key)
    if user is not None:
        return user
    user = _load_user_from_db(api_key)
    if user is not None:
        cache.set_cached_user(api_key, user)
    return user


def is_allowed(user: dict, path: str, method: str) -> bool:
    if not path.startswith(API_PREFIX):
        return False
    resource = path[len(API_PREFIX):].split("/", 1)[0]
    permissions = (user.get("endpoint_access") or {}).get(resource) or {}
    return permissions.get(method.lower(), False) is True


async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    api_key = request.headers.get(API_KEY_HEADER)
    if not api_key:
        return JSONResponse({"detail": "Missing API_KEY header."}, status_code=401)

    user = await run_in_threadpool(find_user, api_key)
    if user is None:
        return JSONResponse({"detail": "Unrecognized API_KEY."}, status_code=401)

    if not is_allowed(user, request.url.path, request.method):
        return JSONResponse(
            {"detail": "API key does not permit this resource and method."},
            status_code=403,
        )

    request.state.user = user
    return await call_next(request)
