from bot.loader import bot_tracker
from telebot.types import Message


@bot_tracker.message_handler(state=None)
def bot_echo(message: Message):
    bot_tracker.reply_to(
        message, f"Эхо без состояния или фильтра.\nСообщение: {message.text}"
    )
