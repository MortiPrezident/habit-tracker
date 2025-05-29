import httpx
from bot.loader import bot_tracker
from telebot.types import Message, CallbackQuery
from bot.auth_services.auth_services import ensure_access
from bot.states.states import CreateHabitState, ViewHabitState
from bot.user_interface.keyboard import KeyboardFactory as Kb
from bot.auth_services.api_client import APIClient
from bot.utils.habit_utils import (
    get_current_habit,
    get_current_text,
    update_data,
    get_current_habit_by_id,
)
from bot.loader import scheduler
from bot.scheduler_task.scheduler_func import send_habit_reminder


@bot_tracker.message_handler(commands=["add_habit"])
async def habit_created(message: Message):
    chat_id = message.chat.id
    access_token = await ensure_access(chat_id)

    if access_token:
        await bot_tracker.set_state(
            message.from_user.id, CreateHabitState.waiting_name, message.chat.id
        )
        await bot_tracker.send_message(
            message.chat.id,
            "📒 Введите название привычки:",
        )
    else:
        await bot_tracker.send_message(
            chat_id,
            "Добро пожаловать! Авторизуйтесь или зарегистрируйтесь.",
            reply_markup=Kb.auth_menu(),
        )


@bot_tracker.message_handler(state=CreateHabitState.waiting_name)
async def process_created_name(message: Message):
    name = message.text.strip()
    await bot_tracker.add_data(message.from_user.id, name=name)
    await bot_tracker.set_state(
        message.from_user.id,
        CreateHabitState.waiting_description_choice,
        message.chat.id,
    )
    await bot_tracker.send_message(
        message.chat.id, "➕ Добавить описание?", reply_markup=Kb.choice_inline()
    )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("choice"),
    state=CreateHabitState.waiting_description_choice,
)
async def process_created_choice(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)

    await bot_tracker.edit_message_reply_markup(
        call.message.chat.id, call.message.id, reply_markup=Kb.ok_inline()
    )

    choice = call.data.split(":")[1]
    if choice == "yes":
        await bot_tracker.set_state(
            call.from_user.id,
            CreateHabitState.waiting_description,
            call.message.chat.id,
        )
        await bot_tracker.send_message(
            call.message.chat.id, "✍️ напишите описание привычки:"
        )
    else:
        await bot_tracker.set_state(
            call.from_user.id, CreateHabitState.waiting_time, call.message.chat.id
        )
        await bot_tracker.send_message(
            call.message.chat.id,
            "⏰ напишите время выполнения привычки в формате 'HH:MM':",
        )


@bot_tracker.message_handler(state=CreateHabitState.waiting_description)
async def process_created_description(message: Message):
    description = message.text
    await bot_tracker.add_data(message.from_user.id, description=description)
    await bot_tracker.set_state(
        message.from_user.id, CreateHabitState.waiting_time, message.chat.id
    )
    await bot_tracker.send_message(
        message.chat.id, "⏰ напишите время выполнения привычки в формате 'HH:MM':"
    )


@bot_tracker.message_handler(state=CreateHabitState.waiting_time)
async def process_created_time(message: Message):
    time = message.text.strip()
    async with bot_tracker.retrieve_data(message.from_user.id) as data:
        name = data["name"]
        description = data.get("description", "")

    data = {
        "name": name,
        "description": description,
        "alert_time": time,
    }
    api = APIClient(message.chat.id)

    resp: httpx.Response = await api.post("/habit/created", json=data)

    if resp.status_code == 200:
        data = resp.json()

        scheduler.add_reminder(
            habit_id=data["id"],
            chat_id=message.chat.id,
            habit_name=data["name"],
            time_str=data["alert_time"],
            callback=send_habit_reminder,
        )

        await bot_tracker.send_message(
            message.chat.id,
            "✅ Вы успешно добавили привычку! Выберете следующее действие",
            reply_markup=Kb.main_menu(),
        )
    else:
        err = resp.json().get("detail", resp.text)
        await bot_tracker.send_message(
            message.chat.id,
            f"❌ Ошибка добавления привычки: {err}. Попробуйте еще раз",
            reply_markup=Kb.main_menu(),
        )

    await bot_tracker.delete_state(message.from_user.id)


@bot_tracker.message_handler(commands=["list_habits"])
async def get_habits(message: Message):
    chat_id = message.chat.id
    access_token = await ensure_access(chat_id)

    api = APIClient(message.chat.id)

    if access_token:
        resp: httpx.Response = await api.get("/habit/habits")
        if resp.status_code == 200:
            data = resp.json()

            await bot_tracker.set_state(
                message.from_user.id, ViewHabitState.viewing_habits, message.chat.id
            )
            await bot_tracker.add_data(
                message.from_user.id, habits=data["habits"], page=1
            )

            if len(data["habits"]) > 0:
                await bot_tracker.send_message(
                    message.chat.id,
                    "📋 Список привычек:",
                    reply_markup=Kb.habits_inline(data["habits"]),
                )
            else:
                await bot_tracker.send_message(
                    message.chat.id, "Вы не добавили пока что не одну привычку"
                )
        else:
            err = resp.json().get("detail", resp.text)
            await bot_tracker.send_message(
                message.chat.id,
                f"❌ Ошибка просмотра привычек: {err}. Попробуйте еще раз",
                reply_markup=Kb.main_menu(),
            )

    else:
        await bot_tracker.send_message(
            chat_id,
            "Добро пожаловать! Авторизуйтесь или зарегистрируйтесь.",
            reply_markup=Kb.auth_menu(),
        )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("habits_page"),
    state=ViewHabitState.viewing_habits,
)
async def pagination(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)

    page = int(call.data.split(":")[1])

    async with bot_tracker.retrieve_data(call.from_user.id) as data:
        habits = data["habits"]

    await bot_tracker.add_data(call.from_user.id, page=page)
    await bot_tracker.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=Kb.habits_inline(habits, page),
    )


@bot_tracker.callback_query_handler(func=lambda call: call.data == "main_menu")
async def detail_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)
    await bot_tracker.delete_message(call.message.chat.id, call.message.id)
    await bot_tracker.send_message(
        call.message.chat.id, "Выберете следующее действие", reply_markup=Kb.main_menu()
    )

    await bot_tracker.delete_state(call.from_user.id)


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("habit_name"),
    state=ViewHabitState.viewing_habits,
)
async def detail_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)

    name = call.data.split(":")[1]

    async with bot_tracker.retrieve_data(call.from_user.id) as data:
        habits = data["habits"]

    habit = get_current_habit(habits, name)
    text = get_current_text(habit)

    await bot_tracker.set_state(
        call.from_user.id, ViewHabitState.viewing_current_habits
    )
    await bot_tracker.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=text,
        reply_markup=Kb.habit_actions(habit["id"], habit["completed"], habit["count"]),
        parse_mode="HTML",
    )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("edit_habit"),
    state=ViewHabitState.viewing_current_habits,
)
async def edit_current_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)

    habit_id = int(call.data.split(":")[1])

    await bot_tracker.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Что хотите изменить❓",
        reply_markup=Kb.edit_choice(habit_id),
    )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("edit:"),
    state=ViewHabitState.viewing_current_habits,
)
async def waiting_name_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)

    habit_id = int(call.data.split(":")[2])

    attribute = call.data.split(":")[1]

    if attribute == "name":
        text = "Введите новое название"
    elif attribute == "description":
        text = "введите новое описание"
    else:
        text = "Введите новое время оповещения в форма 'hh:mm' "

    await bot_tracker.set_state(call.from_user.id, ViewHabitState.edit_name_habit)
    await bot_tracker.add_data(
        call.from_user.id, current_habit_id=habit_id, attribute=attribute
    )
    await bot_tracker.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.id, text=text
    )


@bot_tracker.message_handler(state=ViewHabitState.edit_name_habit)
async def edit_habit(message: Message):
    text = message.text

    api = APIClient(message.chat.id)

    async with bot_tracker.retrieve_data(message.from_user.id) as data:
        habit_id = data["current_habit_id"]
        attribute = data["attribute"]
        habits = data["habits"]

    if attribute == "name":
        data["name"] = text
    elif attribute == "description":
        data["description"] = text
    else:
        data["alert_time"] = text.strip()

    data["id"] = habit_id

    res: httpx.Response = await api.post("/habit/edit", json=data)

    if res.status_code == 200:
        habit = res.json()

        scheduler.add_reminder(
            habit_id=habit["id"],
            chat_id=message.chat.id,
            habit_name=habit["name"],
            time_str=habit["alert_time"],
            callback=send_habit_reminder,
        )

        habits = update_data(habits, habit)

        await bot_tracker.add_data(message.from_user.id, habits=habits)

        text = get_current_text(habit)

        await bot_tracker.set_state(
            message.from_user.id, ViewHabitState.viewing_current_habits
        )

        await bot_tracker.send_message(
            message.chat.id,
            text=text,
            reply_markup=Kb.habit_actions(
                habit["id"], habit["completed"], habit["count"]
            ),
            parse_mode="HTML",
        )
    else:
        err = res.json().get("detail", res.text)
        await bot_tracker.send_message(
            chat_id=message.chat.id,
            text=f"❌ Ошибка редактирования: {err}. Попробуйте еще раз",
            reply_markup=Kb.main_menu(),
        )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data == "habit_complete",
    state=ViewHabitState.viewing_current_habits,
)
async def completed_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(call.id)

    api = APIClient(call.message.chat.id)

    async with bot_tracker.retrieve_data(call.from_user.id) as data:
        id = data["current_habit_id"]
        habits = data["habits"]

    res: httpx.Response = await api.post("/habit/completed", json={"id": id})

    if res.status_code == 200:
        habit = res.json()

        habits = update_data(habits, habit)

        await bot_tracker.add_data(call.from_user.id, habits=habits)

        text = get_current_text(habit)

        await bot_tracker.send_message(
            call.message.chat.id,
            text=text,
            reply_markup=Kb.habit_actions(
                habit["id"], habit["completed"], habit["count"]
            ),
            parse_mode="HTML",
        )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data == "habit_info_back",
    state=ViewHabitState.viewing_current_habits,
)
async def back_to_list_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)

    async with bot_tracker.retrieve_data(call.from_user.id) as data:
        habits = data["habits"]
        page = data["page"]

    await bot_tracker.set_state(call.from_user.id, ViewHabitState.viewing_habits)
    await bot_tracker.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=Kb.habits_inline(habits, page),
    )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("delete_habit"),
    state=ViewHabitState.viewing_current_habits,
)
async def delete_habit(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)
    habit_id = call.data.split(":")[1]

    await bot_tracker.add_data(call.from_user.id, current_habit_id=habit_id)

    await bot_tracker.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Вы уверены, что хотите удалить привычку❓",
        reply_markup=Kb.choice_inline(),
    )


@bot_tracker.callback_query_handler(
    func=lambda call: call.data.startswith("choice"),
    state=ViewHabitState.viewing_current_habits,
)
async def delete_choice(call: CallbackQuery):
    await bot_tracker.answer_callback_query(callback_query_id=call.id)
    choice = call.data.split(":")[1]

    async with bot_tracker.retrieve_data(call.from_user.id) as data:
        habit_id = data["current_habit_id"]
        habits = data["habits"]

    if choice == "yes":
        api = APIClient(call.message.chat.id)
        res: httpx.Response = await api.post(
            "/habit/delete", json={"habit_id": habit_id}
        )
        scheduler.remove_reminder(habit_id=habit_id)
        await bot_tracker.delete_state(call.message.from_user.id)
        if res.status_code == 200:
            await bot_tracker.send_message(
                chat_id=call.message.chat.id,
                text="Привычка удалена. Выберете следующее действие",
                reply_markup=Kb.main_menu(),
            )

        else:
            err = res.json().get("detail", res.text)

            await bot_tracker.send_message(
                chat_id=call.message.chat.id,
                text=f"❌ Ошибка редактирования: {err}. Попробуйте еще раз",
                reply_markup=Kb.main_menu(),
            )
    else:
        habit = get_current_habit_by_id(habits, int(habit_id))
        text = get_current_text(habit)
        await bot_tracker.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=text,
            reply_markup=Kb.habit_actions(habit_id, habit["completed"], habit["count"]),
            parse_mode="HTML",
        )
