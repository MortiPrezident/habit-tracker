from telebot.asyncio_storage.redis_storage import StateRedisStorage
from bot.config_data.config import BOT_TOKEN
from telebot.async_telebot import AsyncTeleBot
from bot.scheduler_task.scheduler import BotScheduler
from bot.config_data.config import DATABASE_URL


redis_storage = StateRedisStorage(host="localhost", port=6379, db=0)
bot_tracker = AsyncTeleBot(token=BOT_TOKEN, state_storage=redis_storage)

scheduler = BotScheduler(DATABASE_URL)
