from envparse import Env

env = Env()
env.read_envfile()

# время хранения токена в редисе
TTL_SECOND = 7 * 24 * 3600

BOT_TOKEN = env.str("BOT_TOKEN")
REDIS_URL = env.str("REDIS_URL")
API_URL = env.str("API_URL")
DATABASE_URL = env.str("SYNC_DATABASE_URL")

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("register", "зарегистрироваться"),
    ("add_habit", "добавить привычку"),
    ("list_habits", "Просмотреть список привычек"),
)
