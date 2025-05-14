import json
from typing import Optional, Dict
from bot.redis.redis_client import get_redis

STATE_TTL_SECONDS = 60 * 60

async def set_state(
        chat_id: int, flow: str, step: str, data: Optional[Dict] = None
) -> None:
    """
    Устанавливает новое состояние диалога для пользователя.

    :param chat_id: chat ID пользователя
    :param flow: имя диалогового потока (например, "register", "add_habit")
    :param step: текущий шаг в рамках потока (например, "waiting_name")
    :param data: дополнительные данные (payload) для этого шага
    """
    redis = await get_redis()
    key = f"state:{chat_id}"
    payload = json.dumps(data or None)
    await redis.hset(
        key, mapping={
            "flow": flow,
            "step": step,
            "data": payload,
        }
    )
    await redis.expire(key, STATE_TTL_SECONDS)

async def get_state(chat_id: int) -> Optional[Dict[str, object]]:
    """
    Получает текущее состояние диалога по chat_id.

    :return: словарь {"flow": str, "step": str, "data": dict} или None, если состояния нет
    """

    redis = await get_redis()
    key = f"state:{chat_id}"
    raw = await redis.hgetall(key)
    if not raw:
        return None
    return {
        "flow": raw.get("flow"),
        "step": raw.get("step"),
        "data": json.loads(raw.get("data", "{}"))
    }

async def clear_state(chat_id: int) -> None:
    """
    Удаляет состояние диалога пользователя (например, при завершении сценария).
    """
    redis = await get_redis()
    await redis.delete(f"state:{chat_id}")