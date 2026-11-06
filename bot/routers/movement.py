# REUNION MOVEMENT

from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..botconfig.keyboards import INLINE_MOVEMENT

router = Router(name="spidor_movement")

DIRECTION_MAP = {
    "move_forward": "forward",
    "move_backward": "backward",
    "move_left": "left",
    "move_right": "right"
}


@router.callback_query(F.data == "show_control")
async def show_control(callback: CallbackQuery):
    await callback.message.edit_text(
        "Movement Control",
        reply_markup=INLINE_MOVEMENT
    )
    await callback.answer()


@router.callback_query(F.data.in_(DIRECTION_MAP))
async def handle_movement(callback: CallbackQuery):
    await callback.message.answer("ok")
    await callback.answer()


@router.callback_query(F.data == "move_stop")
async def handle_stop(callback: CallbackQuery):
    await callback.message.answer("ok")
    await callback.answer()
