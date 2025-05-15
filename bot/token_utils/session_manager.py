from bot.token_utils.redis_client import get_redis
from bot.config_data.config import TTL_SECOND


async def save_tokens(
        chat_id: int, access_token: str, refresh_token: str,
        ttl_seconds:int = TTL_SECOND
):
    """
    Сохраняет access/refresh-token + user_id в Redis с TTL.
    """
    redis = await get_redis()

    key = f"session:{chat_id}"
    await redis.hset(key, mapping={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "chat_id": chat_id
    })

    await redis.expire(key, ttl_seconds)


async def get_tokens(chat_id: int):
    """
    Возвращает dict с полями access_token, refresh_token, user_id
    или {}, если ничего нет в Redis.
    """

    redis = await get_redis()
    key = f"session:{chat_id}"

    data = await redis.hgetall(key)

    return data

async def delete_tokens(chat_id: int):
    """
    Удаляет сессию по chat_id.
    """

    redis = await get_redis()
    key = f"session:{chat_id}"

    await redis.delete(key)


