from aioredis import Redis, from_url
from bot.config_data.config import REDIS_URL

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis

    if _redis is None:
        _redis = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    return _redis
