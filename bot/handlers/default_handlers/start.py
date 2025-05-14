from bot.loader import bot_tracker
from telebot.types import Message
from bot.user_interface.keyboard  import KeyboardFactory as Kb
from bot.auth_services.auth_services import ensure_access


@bot_tracker.message_handler(commands=['start'])
async def cmd_start(message: Message):
    chat_id = message.chat.id

    access_token = await ensure_access(chat_id)

    if access_token:
        await bot_tracker.send_message(
            chat_id,
            "Привет! Что хотите сделать?",
            reply_markup=Kb.main_menu()
        )
    else:
        await bot_tracker.send_message(
            chat_id,
            "Добро пожаловать! Авторизуйтесь или зарегистрируйтесь.",
            reply_markup=Kb.auth_menu()
        )