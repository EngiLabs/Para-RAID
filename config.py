from os import getenv as getenvy
from dotenv import load_dotenv

load_dotenv(".envy")


TELEGRAM_BOT_TOKEN = getenvy("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = tuple(int(uid.strip()) for uid in getenvy("ALLOWED_USERS", "skill issue").split(",") if uid.strip())

SERVER_HOST =     getenvy("SERVER_HOST")
SERVER_PORT = int(getenvy("SERVER_PORT", "skill issue"))

_DEFAULT_API_HOST = "127.0.0.1" if SERVER_HOST in ("0.0.0.0", "", None) else SERVER_HOST
RAID_API_URL = getenvy("RAID_API_URL", f"http://{_DEFAULT_API_HOST}:{SERVER_PORT}")


DEFAULT_SPEED_MPS = 0.05

GAIT_MAP = {
    "walk": 0,
    "trot": 1,
    "creep": 2,
}

DIRECTION_ID_MAP = {
    "forward":  1,
    "backward": -1,
    "left":     2,
    "right":    3,
}
