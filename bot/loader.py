#from telebot.storage import StateMemoryStorage
from config_data.config import BOT_TOKEN
from telebot.async_telebot import AsyncTeleBot

#storage = StateMemoryStorage()
bot_tracker = AsyncTeleBot(token=BOT_TOKEN)
