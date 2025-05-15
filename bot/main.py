import asyncio
from bot.loader import bot_tracker
from utils.set_bot_commands import set_default_commands
from telebot import asyncio_filters
import bot.handlers

async def main():
    bot_tracker.add_custom_filter(asyncio_filters.StateFilter(bot_tracker))
    await set_default_commands(bot_tracker)
    await bot_tracker.polling()

if __name__ == "__main__":
    asyncio.run(main())