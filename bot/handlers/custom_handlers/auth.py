from telebot.types import Message
from bot.loader import bot_tracker
from bot.token_utils.session_manager import save_tokens
import httpx
from bot.config_data.config import API_URL
from bot.user_interface.keyboard import KeyboardFactory as kb
from bot.flow.auth_flow import RegisterFlow, LoginFlow


@bot_tracker.message_handler(commands=["register"])
async def cmd_register(message: Message):
    await bot_tracker.set_state(message.from_user.id, RegisterFlow.waiting_name, message.chat.id)
    await bot_tracker.send_message(
        message.chat.id,
        "📝 Введите логин:",
    )


@bot_tracker.message_handler(state=RegisterFlow.waiting_name)
async def process_register_name(message: Message):
    name = message.text.strip()
    # Сохраняем имя (внутри telebot хранится data автоматически)
    await bot_tracker.add_data(message.chat.id, chat_id=message.chat.id, name=name)
    # Переходим к следующему шагу
    await bot_tracker.set_state(message.from_user.id, RegisterFlow.waiting_password, message.chat.id)
    await bot_tracker.send_message(message.chat.id, "🔑 Придумайте пароль:")


@bot_tracker.message_handler(state=RegisterFlow.waiting_password)
async def process_register_password(message: Message, state):
    chat_id = message.chat.id
    data = await bot_tracker.get_data(message.chat.id)
    username = data["name"]
    password = message.text.strip()

    # … отправляем на API, сохраняем токены …
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/auth/register",
            json={
                "name": username,
                "password": password,
                "chat_id": chat_id
            }
        )
    if resp.status_code == 200:
        data = resp.json()
        await save_tokens(chat_id, data["access_token"], data["refresh_token"])
        await bot_tracker.send_message(chat_id, "✅ Регистрация прошла успешно! Выберете следующее действие", reply_markup=kb.main_menu())
    else:
        err = resp.json().get("detail", resp.text)
        await bot_tracker.send_message(chat_id, f"❌ Ошибка регистрации: {err}. Попробуйте ещё раз", reply_markup=kb.auth_menu())


    await bot_tracker.finish_state(message.chat.id)  # сброс FSM





@bot_tracker.message_handler(commands=["login"])
async def cmd_login(message: Message):
    chat_id = message.chat.id

    await bot_tracker.set_state(message.from_user.id, LoginFlow.waiting_name, message.chat.id)
    await bot_tracker.send_message(chat_id, "👤 Введите ваш логин:")


@bot_tracker.message_handler(state=LoginFlow.waiting_name)
async def process_login_name(message: Message, state):
    chat_id = message.chat.id
    name = message.text.strip()
    # Сохраняем имя (внутри telebot хранится data автоматически)
    await bot_tracker.update_data(chat_id, name=name)
    # Переходим к следующему шагу
    await bot_tracker.set_state(message.from_user.id, LoginFlow.waiting_password, message.chat.id)
    await bot_tracker.send_message(chat_id, "🔑 Введите ваш пароль:")


@bot_tracker.message_handler(state=LoginFlow.waiting_password)
async def process_login_password(message: Message, state):
    chat_id = message.chat.id
    data = await bot_tracker.get_data(message.chat.id)
    username = data["name"]
    password = message.text.strip()

    # … отправляем на API, сохраняем токены …
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/auth/login",
            json={
                "name": username,
                "password": password
            }
        )

    if resp.status_code == 200:
        data = resp.json()
        await save_tokens(chat_id, data["access_token"], data["refresh_token"])
        await bot_tracker.send_message(chat_id,"✅ Вы успешно вошли! Выберете следующее действие", reply_markup=kb.main_menu())
    else:
        err = resp.json().get("detail", resp.text)
        await bot_tracker.send_message(chat_id,f"❌ Ошибка входа: {err}. Попробуйте еще раз",reply_markup=kb.auth_menu(),
        )

    await bot_tracker.finish_state(message.chat.id)  # сброс FSM
