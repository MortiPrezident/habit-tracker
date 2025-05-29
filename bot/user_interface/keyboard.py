import math

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


class KeyboardFactory:
    @staticmethod
    def auth_menu() -> ReplyKeyboardMarkup:
        """
        Возвращает клавиатуру для неавторизованного пользователя:
        /register, /login
        """
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton("/register"), KeyboardButton("/login"))
        return kb

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """
        Возвращает основное меню для авторизованного пользователя:
        /add_habit, /list_habits
        """
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton("/add_habit"), KeyboardButton("/list_habits"))
        return kb

    @staticmethod
    def choice_inline() -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=2)

        kb.add(
            InlineKeyboardButton(text="✅ Да!", callback_data="choice:yes"),
            InlineKeyboardButton(text="❌ Нет!", callback_data="choice:no"),
        )

        return kb

    @staticmethod
    def ok_inline() -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton(text="✅ OK", callback_data="noop"))

        return kb

    @staticmethod
    def render_postgres_bar(count: int, length: int = 21) -> str:
        filled = min(count, length)
        empty = max(length - filled, 0)
        return "🟩" * filled + "⬜" * empty

    @staticmethod
    def habits_inline(
        habits: list[dict],
        page: int = 1,
        page_size: int = 5,
    ) -> InlineKeyboardMarkup:
        """
        Inline-клавиатура для списка привычек с прогресс-баром и пагинацией.

        :param habits: список привычек
        :param page: текущая страница (начиная с 1)
        :param page_size: количество привычек на странице
        """
        kb = InlineKeyboardMarkup(row_width=1)
        total = len(habits)
        total_pages = math.ceil(total / page_size)

        page = min(page, total_pages)

        start = (page - 1) * page_size
        end = start + page_size
        page_habits = habits[start:end]
        # Добавляем кнопки привычек
        for habit in page_habits:
            bar = KeyboardFactory.render_postgres_bar(habit["count"])
            text = f"{habit['name']} [{bar}]"
            kb.add(
                InlineKeyboardButton(
                    text=text, callback_data=f"habit_name:{habit['name']}"
                )
            )

        nav = []

        if page > 1:
            nav.append(
                InlineKeyboardButton(
                    text="◀️ Назад", callback_data=f"habits_page:{page - 1}"
                )
            )
        if page < total_pages:
            nav.append(
                InlineKeyboardButton(
                    text="▶️ Вперёд", callback_data=f"habits_page:{page + 1}"
                )
            )

        if nav:
            kb.row(*nav)

        kb.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))

        return kb

    @staticmethod
    def habit_actions(
        habit_id: int, completed: bool, count: int
    ) -> InlineKeyboardMarkup:
        """
        Inline-клавиатура для действий над конкретной привычкой
        """

        kb = InlineKeyboardMarkup(row_width=2)
        if not completed and count < 21:
            kb.add(
                InlineKeyboardButton(text="Выполнить", callback_data=f"habit_complete")
            )
        kb.add(
            InlineKeyboardButton(
                text="Редактировать", callback_data=f"edit_habit:{habit_id}"
            ),
            InlineKeyboardButton(
                text="Удалить", callback_data=f"delete_habit:{habit_id}"
            ),
            InlineKeyboardButton(text="Назад", callback_data=f"habit_info_back"),
        )
        return kb

    @staticmethod
    def edit_choice(habit_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(
                text="Название", callback_data=f"edit:name:{habit_id}"
            ),
            InlineKeyboardButton(
                text="описание", callback_data=f"edit:description:{habit_id}"
            ),
            InlineKeyboardButton(
                text="время оповещения", callback_data=f"edit:time:{habit_id}"
            ),
            InlineKeyboardButton(text="назад", callback_data="edit_back"),
        )

        return kb
