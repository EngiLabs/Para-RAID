from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router(name="spidor_camera")


@router.message(Command("photo"))
async def photo_cmd(message: Message):
    await message.answer("ok")


@router.callback_query(F.data == "req_photo")
async def photo_cb(callback: CallbackQuery):
    await callback.message.answer("ok")
    await callback.answer()
