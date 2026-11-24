from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from ..api_client import raid_api

router = Router(name="spidor_camera")


async def actual_proceed_photo(message_link: Message):
    frame, err = await raid_api.capture_photo()
    if frame:
        await message_link.answer_photo(photo=BufferedInputFile(
            file=frame,
            filename="frame.jpg"
        ))
    elif err:
        await message_link.answer(f"can't get a photo from the unit ({err})")
    else:
        await message_link.answer("a photo from the unit was corrupted")


@router.message(Command("photo"))
async def photo_cmd(message: Message):
    await actual_proceed_photo(message)


@router.callback_query(F.data == "req_photo")
async def photo_cb(callback: CallbackQuery):
    await actual_proceed_photo(callback.message)
    await callback.answer()
