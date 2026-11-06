from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

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


async def update_bot_stats(bot: Bot):
    from .botconfig.data import NAME, COMMANDS

    await bot.set_my_name(name=NAME[0], language_code=NAME[1])
    await bot.set_my_commands([BotCommand(command=cmd[0], description=cmd[1]) for cmd in COMMANDS])
