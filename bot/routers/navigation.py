from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from vision.navigator import Navigator

router = Router(name="spidor_navigation")
navigator = Navigator()


@router.message(Command("home"))
async def home_cmd(message: Message):
    await message.answer("ok")


@router.callback_query(F.data == "cmd_home")
async def home_cb(callback: CallbackQuery):
    await callback.message.answer("ok")
    await callback.answer()


@router.message(Command("goto"))
async def goto_cmd(message: Message):
    await message.answer("ok")
