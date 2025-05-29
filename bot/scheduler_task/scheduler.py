from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from bot.config_data.config import API_URL
from typing import Callable
import logging
import httpx

logging.basicConfig(level=logging.INFO)


class BotScheduler:
    def __init__(self, db_url: str):
        executors = {"default": AsyncIOExecutor()}
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": SQLAlchemyJobStore(url=db_url)}, executors=executors
        )
        logging.info("BotScheduler init")

    def start(self):
        """Запускает планировщик"""
        self.scheduler.start()
        logging.info("BotScheduler started")

    def add_reminder(
        self,
        habit_id: int,
        chat_id: int,
        habit_name: str,
        time_str: str,
        callback: Callable[[int, int, str], None],
    ):
        """
        Запланировать ежедневное напоминание:
         - chat_id: куда шлём (Telegram chat ID)
         - habit_id: для идентификации и удаления
         - habit_name: чтобы в сообщении выводить название
         - time_str: 'HH:MM'
         - callback: функция вида async def callback(chat_id, habit_id, habit_name)
        """
        hour, minute, _ = map(int, time_str.split(":"))
        job_id = f"habit-{habit_id}"

        # replace_existing=True перезапишет старую задачу (если была) новой
        self.scheduler.add_job(
            func=callback,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[chat_id, habit_id, habit_name],
            id=job_id,
            replace_existing=True,
        )
        logging.info(f"📌 Задача на привычку {habit_id} добавлена для юзера {chat_id}")

    def remove_reminder(self, habit_id: int):
        job_id = f"habit-{habit_id}"

        try:
            self.scheduler.remove_job(job_id)
            logging.info(f"❌ задача удалена: {job_id}")
        except Exception:
            logging.warning(f"задача {job_id} не найдена при удалении")

    async def sync_with_db(self, func: Callable):
        """
        Синхронизирует задачи в планировщике с привычками из базы данных:
        - Добавляет задачи для всех привычек из базы.
        - Удаляет задачи, для которых привычек нет в базе.
        """
        try:
            # Получаем все привычки из базы
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{API_URL}/habit/habits_all")
            resp.raise_for_status()
            data = resp.json()
            habits = data["habits"]
        except Exception as e:
            logging.error(f"Ошибка при получении привычек: {e}")
            return

        existing_job_ids = {job.id for job in self.scheduler.get_jobs()}

        db_job_ids = set()
        for habit in habits:
            habit_id = habit["habit_id"]
            job_id = f"habit-{habit_id}"
            db_job_ids.add(job_id)

            self.add_reminder(
                habit_id=habit_id,
                chat_id=habit["chat_id"],
                habit_name=habit["habit_name"],
                time_str=habit["time_str"],
                callback=func,
            )

        for job_id in existing_job_ids - db_job_ids:
            try:
                self.scheduler.remove_job(job_id)
                logging.info(f"🧹 Удалена устаревшая задача: {job_id}")
            except Exception as e:
                logging.warning(f"⚠️ Не удалось удалить задачу: {job_id}. Ошибка {e}")

    def add_daily_decrement_job(self, func: Callable):
        """
        Ставит задачу на каждую ночь в 23:59,
        которая вызовет POST /habit/decrease_uncompleted.
        """

        # Оборачиваем в lambda, чтобы APScheduler знал обычную функцию
        self.scheduler.add_job(
            func=func,
            trigger=CronTrigger(hour=23, minute=59),
            id="decrement_habits_job",
            replace_existing=True,
        )
        logging.info(
            "📅 Ежедневная задача decrement_uncompleted запланирована на 23:59"
        )
