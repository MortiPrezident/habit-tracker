import asyncio
from bot.loader import bot_tracker
from utils.set_bot_commands import set_default_commands
from telebot import asyncio_filters
from bot.loader import scheduler
from bot.scheduler_task.scheduler_func import send_habit_reminder, call_decrement
import bot.handlers


async def main():
    bot_tracker.add_custom_filter(asyncio_filters.StateFilter(bot_tracker))
    await set_default_commands(bot_tracker)
    scheduler.start()
    await scheduler.sync_with_db(send_habit_reminder)
    scheduler.add_daily_decrement_job(call_decrement)
    await bot_tracker.polling()


if __name__ == "__main__":
    asyncio.run(main())
