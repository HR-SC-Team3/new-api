import hashlib
import json
import logging
import os

import redis
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

API_KEY_TTL_SECONDS = 60

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        load_dotenv()
        _client = redis.Redis.from_url(
            os.environ["REDIS_URL"],
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
    return _client


def _key(api_key: str) -> str:
    # Hash the key so the raw secret never appears in Redis key names.
    return "auth:apikey:" + hashlib.sha256(api_key.encode()).hexdigest()


def get_cached_user(api_key: str) -> dict | None:
    """Return {"app", "endpoint_access"} from Redis, or None on a miss or Redis error."""
    try:
        raw = get_redis().get(_key(api_key))
    except redis.RedisError:
        logger.warning("Redis unavailable, falling back to PostgreSQL", exc_info=True)
        return None
    return json.loads(raw) if raw else None


def set_cached_user(api_key: str, user: dict) -> None:
    try:
        get_redis().set(_key(api_key), json.dumps(user), ex=API_KEY_TTL_SECONDS)
    except redis.RedisError:
        logger.warning("Redis unavailable, user not cached", exc_info=True)


def invalidate_api_key(api_key: str) -> None:
    """Call this after any write that changes or removes a user."""
    try:
        get_redis().delete(_key(api_key))
    except redis.RedisError:
        logger.warning("Redis unavailable, cache not invalidated", exc_info=True)
