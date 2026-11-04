from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.config.keyboards import INLINE_MAIN

router = Router(name="spidor_start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "SPIDOR Control Panel!\n\n"
        "/help = available commands.",
        reply_markup=INLINE_MAIN
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("""
Available commands:
/start
/status
/photo
/goto
/help
"""
                         )
