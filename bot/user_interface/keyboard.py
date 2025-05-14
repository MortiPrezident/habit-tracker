from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class KeyboardFactory:

    @staticmethod
    def auth_menu() -> ReplyKeyboardMarkup:
        """
        Возвращает клавиатуру для неавторизованного пользователя:
        /register, /login
        """
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(
            KeyboardButton("/register"),
            KeyboardButton("/login")
        )
        return kb


    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """
        Возвращает основное меню для авторизованного пользователя:
        /add_habit, /list_habits
        """
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(
            KeyboardButton("/add_habit"),
            KeyboardButton("/list_habits")
        )
        return kb

    @staticmethod
    def habits_inline(habits: list[dict]) -> InlineKeyboardMarkup:
        """
        Inline-клавиатура для списка привычек.
        habits: список словарей с ключами 'id' и 'name'
        """
        kb = InlineKeyboardMarkup(row_width=1)
        for h in habits:
            kb.add(
                InlineKeyboardButton(
                    text=h.get("name", "Без названия"),
                    callback_data=f"habit:{h.get('id')}"
                )
            )
        return kb

    @staticmethod
    def habit_actions(habit_id: int) -> InlineKeyboardMarkup:
        """
        Inline-клавиатура для действий над конкретной привычкой
        """

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(
                text="Редактировать",
                callback_data=f"delete_habit:{habit_id}"
            ),
            InlineKeyboardButton(
                text="Удалить",
                callback_data=f"delete_habit:{habit_id}"
            )
        )
        return kb

    @staticmethod
    def confirm_action(action: str, item_id: int) -> InlineKeyboardMarkup:
        """
        Inline-клавиатура для подтверждения действия (Да/Нет).
        action: текстовое имя действия, например 'delete_habit'.
        """
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Да", callback_data=f"confirm:{action}:{item_id}"),
            InlineKeyboardButton("❌ Нет", callback_data=f"cancel:{action}:{item_id}")
        )
        return kb