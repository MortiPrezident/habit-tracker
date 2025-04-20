from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand
from bot.config_data.config import DEFAULT_COMMANDS

async def set_default_commands(bot_traker: AsyncTeleBot):
    await bot_traker.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )