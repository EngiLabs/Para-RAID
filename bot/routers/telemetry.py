from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router(name="spidor_telemetry")


@router.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer("ok")


@router.callback_query(F.data == "req_status")
async def cb_status(callback: CallbackQuery):
    await callback.message.answer("ok")
    await callback.answer()
