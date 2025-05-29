from bot.auth_services.api_client import APIClient
from bot.loader import scheduler
import httpx
from bot.config_data.config import API_URL
import logging


async def call_decrement():
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/habit/decrease_uncompleted")
    except Exception as e:
        logging.error(f"Ошибка decrement_uncompleted: {e}")


async def send_habit_reminder(chat_id: int, habit_id: int, habit_name: str):
    from bot.loader import bot_tracker

    api = APIClient(chat_id)
    resp = await api.get("/habit/check", json={"id": habit_id})
    data = resp.json()

    if not data["completed"] and data["count"] < 21:
        await bot_tracker.send_message(
            chat_id,
            f"🔔 Пора выполнить привычку: *{habit_name}*",
            parse_mode="Markdown",
        )
    elif data["completed"]:
        return
    else:
        scheduler.remove_reminder(habit_id)
