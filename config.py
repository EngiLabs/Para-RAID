from os import getenv as getenvy
from dotenv import load_dotenv

load_dotenv(".envy")


TELEGRAM_BOT_TOKEN = getenvy("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = (int(uid.strip()) for uid in getenvy("ALLOWED_USERS", "skill issue").split(",") if uid.strip())

SERVER_HOST =     getenvy("SERVER_HOST")
SERVER_PORT = int(getenvy("SERVER_PORT", "skill issue"))
