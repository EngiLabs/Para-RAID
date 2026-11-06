from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config as global_config
from .routers import start, movement, telemetry, camera, navigation


def create_bot() -> Bot:
    return Bot(
        token=global_config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
        start.router,
        movement.router,
        telemetry.router,
        camera.router,
        navigation.router
    )
    return dp
