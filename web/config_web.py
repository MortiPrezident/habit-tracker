from envparse import Env

env = Env()
env.read_envfile()

DATABASE_URL = env.str("DATABASE_URL")
