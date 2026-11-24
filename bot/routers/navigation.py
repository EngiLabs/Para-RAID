from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from ..api_client import raid_api

router = Router(name="spidor_navigation")


@router.message(Command("home"))
async def home_cmd(message: Message):
    ok = await raid_api.home()
    await message.answer("got it" if ok else "an error occured during home call")


@router.callback_query(F.data == "cmd_home")
async def home_cb(callback: CallbackQuery):
    ok = await raid_api.home()
    await callback.message.answer("got it" if ok else "an error occured during home call")
    await callback.answer()


@router.message(Command("goto"))
async def goto_cmd(message: Message):
    parts = (message.text or "").split()
    if len(parts) < 3:
        await message.answer("usage: /goto <x> <y>")
        return
    try:
        x, y = float(parts[1]), float(parts[2])
    except ValueError:
        await message.answer("invalid coordinates, usage: /goto <x> <y>")
        return
    ok = await raid_api.navigate_to(x, y)
    await message.answer(f"📍 navigating to ({x}, {y})" if ok else "an error occured during goto call")
