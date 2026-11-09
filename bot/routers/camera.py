from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from core import raid, state_snapshot

router = Router(name="spidor_camera")


async def actual_proceed_photo(message_link: Message):
    if await raid.capture_photo():
        await message_link.answer_photo(photo=BufferedInputFile(
            file=state_snapshot.last_frame,
            filename="frame.jpg"
        ))
    else:
        await message_link.answer("can't get a photo from the unit")


@router.message(Command("photo"))
async def photo_cmd(message: Message):
    await actual_proceed_photo(message)


@router.callback_query(F.data == "req_photo")
async def photo_cb(callback: CallbackQuery):
    await actual_proceed_photo(callback.message)
    await callback.answer()
