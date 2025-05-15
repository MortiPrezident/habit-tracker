from telebot.asyncio_storage.redis_storage import StateRedisStorage
from bot.config_data.config import BOT_TOKEN
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters

redis_storage = StateRedisStorage(host='localhost', port=6379, db=0)
bot_tracker = AsyncTeleBot(token=BOT_TOKEN, state_storage=redis_storage)

