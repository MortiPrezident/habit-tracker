from envparse import Env

env = Env()
env.read_envfile()

BOT_TOKEN = env.str("BOT_TOKEN")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
)
