def get_current_habit_by_id(habits: list[dict], habit_id: int) -> dict:
    for habit in habits:
        if habit["id"] == habit_id:
            return habit

    return {}


def get_current_habit(habits: list[dict], current_name) -> dict:
    for habit in habits:
        if habit["name"] == current_name:
            return habit

    return {}


def get_current_text(habit: dict) -> str:
    name = habit.get("name", "Без названия")
    description = habit.get("description", "Описание отсутствует")
    alert_time = habit.get("alert_time", "00:00")
    count = habit.get("count", 0)

    completed = habit.get("completed", False)

    if not completed and count != 21:
        completed_text = f"⌛️<b>Сегодня ещё не выполнили</b>😢"
    elif count == 21:
        completed_text = f"🤩<b>привычка закреплена</b>🤩"
    else:
        completed_text = f"⌛️<b>Сегодня привычка выполнена</b>😊"

    text = (
        f"<b>ℹ️ Информация о привычке!</b>\n\n"
        f"🌱 <b>{name}</b>\n\n"
        f"📝 <b>Описание:</b> {description or '—'}\n"
        f"⏰ <b>Напоминание:</b> {alert_time}\n"
        f"✅ <b>Выполнено раз:</b> {count} из 21\n"
        f"{completed_text}"
    )

    return text


def update_data(habits: list[dict], habit: dict) -> dict:
    id = habit["id"]

    for index in range(len(habits)):
        if id == habits[index]["id"]:
            habits[index] = habit
            break

    return habits
