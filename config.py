from os import getenv as getenvy
from dotenv import load_dotenv

load_dotenv(".envy")


TELEGRAM_BOT_TOKEN = getenvy("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = (int(uid.strip()) for uid in getenvy("ALLOWED_USERS", "skill issue").split(",") if uid.strip())

SERVER_HOST =     getenvy("SERVER_HOST")
SERVER_PORT = int(getenvy("SERVER_PORT", "skill issue"))


DEFAULT_SPEED_MPS = 0.05

GAIT_MAP = {
    "walk": 0,
    "trot": 1,
    "creep": 2,
}

DIRECTION_VECTOR_MAP = {
    "forward":  {"direction": 1,  "vy": 1,  "vx": 0,  "vr": 0},
    "backward": {"direction": -1, "vy": -1, "vx": 0,  "vr": 0},
    "left":     {"direction": 2,  "vy": 0,  "vx": -1, "vr": 0},
    "right":    {"direction": 3,  "vy": 0,  "vx": 1,  "vr": 0},
}
