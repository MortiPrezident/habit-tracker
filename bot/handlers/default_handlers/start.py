import httpx
from bot.loader import bot_tracker
from telebot.types import Message

@bot_tracker.message_handler(commands=['help', 'start'])
async def send_welcome(message: Message):

    async with httpx.AsyncClient() as client:
        response = await client.get("http://0.0.0.0:5000/hello")
    text = response.text
    await bot_tracker.reply_to(message, text)