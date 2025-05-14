from telebot.handler_backends import StatesGroup, State


class RegisterFlow(StatesGroup):
    waiting_name     = State()  # этап, на котором бот ждёт логин
    waiting_password = State()  # этап, на котором бот ждёт пароль

class LoginFlow(StatesGroup):
    waiting_name     = State()  # бот ждёт ввод логина
    waiting_password = State()  # бот ждёт ввод пароля