from telebot.types import Message
from bot.loader import bot_tracker
from bot.token_utils.session_manager import save_tokens
import httpx
from bot.config_data.config import API_URL
from bot.states.states import RegisterState, LoginState
from bot.auth_services.auth_services import ensure_access
from bot.user_interface.keyboard import KeyboardFactory as Kb


@bot_tracker.message_handler(commands=["register"])
async def cmd_register(message: Message):
    chat_id = message.chat.id

    access_token = await ensure_access(chat_id)

    if access_token:
        await bot_tracker.send_message(
            chat_id, "Привет! Что хотите сделать?", reply_markup=Kb.main_menu()
        )
    else:
        await bot_tracker.set_state(
            message.from_user.id, RegisterState.waiting_name, message.chat.id
        )
        await bot_tracker.send_message(
            message.chat.id,
            "📝 Введите логин:",
        )


@bot_tracker.message_handler(state=RegisterState.waiting_name)
async def process_register_name(message: Message):
    name = message.text.strip()
    # Сохраняем имя (внутри telebot хранится data автоматически)
    await bot_tracker.add_data(message.from_user.id, name=name)
    # Переходим к следующему шагу
    await bot_tracker.set_state(
        message.from_user.id, RegisterState.waiting_password, message.chat.id
    )
    await bot_tracker.send_message(message.chat.id, "🔑 Придумайте пароль:")


@bot_tracker.message_handler(state=RegisterState.waiting_password)
async def process_register_password(message: Message):
    chat_id = message.chat.id

    async with bot_tracker.retrieve_data(message.from_user.id) as data:
        username = data["name"]
    password = message.text.strip()
    await bot_tracker.delete_message(message.chat.id, message.id)
    print(API_URL, type(API_URL))

    # … отправляем на API, сохраняем токены …
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/auth/register",
            json={"name": username, "password": password, "chat_id": chat_id},
        )
    if resp.status_code == 200:
        data = resp.json()
        await save_tokens(data["chat_id"], data["access_token"], data["refresh_token"])
        await bot_tracker.send_message(
            chat_id,
            "✅ Регистрация прошла успешно! Выберете следующее действие",
            reply_markup=Kb.main_menu(),
        )
    else:
        err = resp.json().get("detail", resp.text)
        await bot_tracker.send_message(
            chat_id,
            f"❌ Ошибка регистрации: {err}. Попробуйте ещё раз",
            reply_markup=Kb.auth_menu(),
        )

    await bot_tracker.delete_state(message.from_user.id)  # сброс FSM


@bot_tracker.message_handler(commands=["login"])
async def cmd_login(message: Message):
    chat_id = message.chat.id

    access_token = await ensure_access(chat_id)

    if access_token:
        await bot_tracker.send_message(
            chat_id, "Привет! Что хотите сделать?", reply_markup=Kb.main_menu()
        )
    else:
        await bot_tracker.set_state(
            message.from_user.id, LoginState.waiting_name, message.chat.id
        )
        await bot_tracker.send_message(chat_id, "👤 Введите ваш логин:")


@bot_tracker.message_handler(state=LoginState.waiting_name)
async def process_login_name(message: Message):
    chat_id = message.chat.id
    name = message.text.strip()
    # Сохраняем имя (внутри telebot хранится data автоматически)
    await bot_tracker.add_data(message.from_user.id, name=name)
    # Переходим к следующему шагу
    await bot_tracker.set_state(
        message.from_user.id, LoginState.waiting_password, message.chat.id
    )
    await bot_tracker.send_message(chat_id, "🔑 Введите ваш пароль:")


@bot_tracker.message_handler(state=LoginState.waiting_password)
async def process_login_password(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    async with bot_tracker.retrieve_data(message.from_user.id) as data:
        username = data["name"]
    password = message.text.strip()
    await bot_tracker.delete_message(message.chat.id, message.id)
    # … отправляем на API, сохраняем токены …
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/auth/login", json={"name": username, "password": password}
        )

    if resp.status_code == 200:
        data = resp.json()
        await save_tokens(data["chat_id"], data["access_token"], data["refresh_token"])
        await bot_tracker.send_message(
            chat_id,
            "✅ Вы успешно вошли! Выберете следующее действие",
            reply_markup=Kb.main_menu(),
        )
    else:
        err = resp.json().get("detail", resp.text)
        await bot_tracker.send_message(
            chat_id,
            f"❌ Ошибка входа: {err}. Попробуйте еще раз",
            reply_markup=Kb.auth_menu(),
        )

    await bot_tracker.delete_state(message.from_user.id)  # сброс FSM
