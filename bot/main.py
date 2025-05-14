import asyncio
from bot.loader import bot_tracker
from utils.set_bot_commands import set_default_commands
from telebot.custom_filters import StateFilter
import bot.handlers

async def main():
    #await set_default_commands(bot_tracker)
    await bot_tracker.polling()

if __name__ == "__main__":
    asyncio.run(main())