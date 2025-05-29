from telebot.handler_backends import StatesGroup, State


class RegisterState(StatesGroup):
    waiting_name = State()  # этап, на котором бот ждёт логин
    waiting_password = State()  # этап, на котором бот ждёт пароль


class LoginState(StatesGroup):
    waiting_name = State()  # бот ждёт ввод логина
    waiting_password = State()  # бот ждёт ввод пароля


class CreateHabitState(StatesGroup):
    waiting_name = State()
    waiting_description_choice = State()
    waiting_description = State()
    waiting_time = State()


class ViewHabitState(StatesGroup):
    viewing_habits = State()
    viewing_current_habits = State()
    edit_name_habit = State()
