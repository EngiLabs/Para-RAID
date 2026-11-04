from aiogram import Bot, Dispatcher

import config as global_config
from .routers import start, movement, telemetry, camera, navigation


def create_bot() -> Bot:
    return Bot(token=global_config.TELEGRAM_BOT_TOKEN)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_routers(
        start.router,
        movement.router,
        telemetry.router,
        camera.router,
        navigation.router
    )
    return dp
